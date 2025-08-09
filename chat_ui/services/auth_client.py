from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

import requests
from PyQt6.QtCore import QSettings

from chat_ui.services.local_gsi_server import get_id_token_via_local_gsi
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    _HAS_INSTALLED_FLOW = True
except Exception:
    _HAS_INSTALLED_FLOW = False


def _load_frontend_config() -> Dict[str, Any]:
    # Load chat_ui/config.json if present
    config_path = Path(__file__).resolve().parents[1] / "config.json"
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


_CFG = _load_frontend_config()

BACKEND_BASE_URL = _CFG.get("backend_base_url") or os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")


@dataclass
class LoginResult:
    success: bool
    session_token: Optional[str] = None
    requires_registration: bool = False
    message: Optional[str] = None
    id_token: Optional[str] = None
    token_email: Optional[str] = None
    token_sub: Optional[str] = None
    token_first_name: Optional[str] = None
    token_last_name: Optional[str] = None


class AuthClient:
    ORG = "NeuraFormAI"
    APP = "NeuraPal"
    KEY = "session_token"

    def __init__(self):
        self.settings = QSettings(self.ORG, self.APP)
        self.session_token: Optional[str] = self.settings.value(self.KEY, type=str)
        self._profile_cache: Optional[Dict[str, Any]] = None

    def set_session_token(self, token: str) -> None:
        self.session_token = token
        self.settings.setValue(self.KEY, token)

    def clear_session_token(self) -> None:
        self.session_token = None
        self.settings.remove(self.KEY)
        self._profile_cache = None

    def get_headers(self) -> Dict[str, str]:
        if not self.session_token:
            return {"Content-Type": "application/json"}
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.session_token}",
        }

    def validate_session(self) -> bool:
        if not self.session_token:
            return False
        try:
            r = requests.get(
                f"{BACKEND_BASE_URL}/auth/profile",
                headers=self.get_headers(),
                timeout=10,
            )
            if r.status_code == 200:
                try:
                    self._profile_cache = r.json()
                except Exception:
                    self._profile_cache = None
                return True
            # Any non-200 means the stored token is not usable; clear it so UI can prompt login
            self.clear_session_token()
            return False
        except Exception:
            # Network or other failure: treat as invalid so we re-auth
            self.clear_session_token()
            return False

    def fetch_profile(self) -> Optional[Dict[str, Any]]:
        if not self.session_token:
            return None
        try:
            r = requests.get(
                f"{BACKEND_BASE_URL}/auth/profile",
                headers=self.get_headers(),
                timeout=10,
            )
            if r.status_code == 200:
                self._profile_cache = r.json()
                return self._profile_cache
            return None
        except Exception:
            return None

    def get_user_id(self) -> Optional[str]:
        if self._profile_cache and isinstance(self._profile_cache, dict):
            uid = self._profile_cache.get("id")
            if isinstance(uid, str) and uid:
                return uid
        prof = self.fetch_profile()
        if prof and isinstance(prof, dict):
            uid = prof.get("id")
            if isinstance(uid, str) and uid:
                return uid
        return None

    def _desktop_google_flow(self) -> str:
        client_id = _CFG.get("google_client_id") or os.getenv("GOOGLE_CLIENT_ID")
        client_secret = _CFG.get("google_client_secret") or os.getenv("GOOGLE_CLIENT_SECRET")
        if not client_id:
            raise RuntimeError("Google client ID not set. Edit chat_ui/config.json (google_client_id).")

        # If a desktop client secret is provided, use the Installed App flow (same as the working script)
        if client_secret:
            if not _HAS_INSTALLED_FLOW:
                raise RuntimeError("google-auth-oauthlib is required for Desktop flow. Install it in your venv.")
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"],
                }
            }
            scopes = [
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
            ]
            flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
            creds = flow.run_local_server(port=0)
            if not getattr(creds, "id_token", None):
                raise RuntimeError("No ID token from Google")
            return creds.id_token

        # Otherwise, use the local GSI page (client_id only)
        return get_id_token_via_local_gsi(client_id)

    def _decode_id_token(self, id_token: str) -> Dict[str, Any]:
        r = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def login_with_google(self) -> LoginResult:
        id_token = self._desktop_google_flow()
        try:
            info = self._decode_id_token(id_token)
        except Exception:
            info = {}
        payload = {
            "provider": "google",
            "token": id_token,
            "device_info": {"platform": "desktop", "ui": "pyqt"},
        }
        r = requests.post(f"{BACKEND_BASE_URL}/auth/login", json=payload, timeout=20)
        if r.status_code != 200:
            return LoginResult(success=False, message=f"login_http_{r.status_code}")
        data = r.json()
        if data.get("success") and data.get("session_token"):
            self.set_session_token(data["session_token"])
            return LoginResult(success=True, session_token=data["session_token"]) 
        if data.get("requires_registration"):
            return LoginResult(
                success=False,
                requires_registration=True,
                id_token=id_token,
                token_email=info.get("email"),
                token_sub=info.get("sub"),
                token_first_name=info.get("given_name"),
                token_last_name=info.get("family_name"),
            )
        return LoginResult(success=False, message=data.get("message"))

    def complete_registration(
        self,
        provider_user_id: str,
        first_name: str,
        last_name: str,
        email: str,
        birthdate: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        payload = {
            "provider": "google",
            "provider_user_id": provider_user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "birthdate": birthdate,
        }
        r = requests.post(f"{BACKEND_BASE_URL}/auth/register", json=payload, timeout=20)
        if r.status_code != 200:
            try:
                msg = r.json().get("detail")
            except Exception:
                msg = r.text
            return False, None, msg
        data = r.json()
        token = data.get("session_token")
        if token:
            self.set_session_token(token)
            return True, token, None
        return False, None, "no_session_token"


auth_client = AuthClient()


