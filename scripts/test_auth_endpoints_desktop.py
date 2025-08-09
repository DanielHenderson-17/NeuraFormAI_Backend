"""
Desktop OAuth tester for Google (no Web client needed).

What it does:
- Uses your Desktop OAuth client (client ID/secret from .env) via the Installed App flow
- Obtains an ID token, then calls your backend:
  1) POST /auth/login
  2) If registration required, prompts for birthdate and POST /auth/register
  3) GET /auth/profile with the returned session token

Run via: test_auth_desktop.bat

Env required (already in your .env):
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET
- BACKEND_BASE_URL (optional, defaults to http://127.0.0.1:8000)
"""

from __future__ import annotations

import os
import json
from datetime import date

import requests
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow


load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
ALLOWED_GOOGLE_IDS = os.getenv("GOOGLE_CLIENT_IDS") or os.getenv("GOOGLE_CLIENT_ID") or ""

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("ERROR: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set in .env")
    raise SystemExit(1)


def get_id_token_via_desktop_flow() -> str:
    client_config = {
        "installed": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [
                "http://localhost"
            ],
        }
    }

    # Use Google's full scope URIs to avoid scope-mismatch exception
    scopes = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
    flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
    creds = flow.run_local_server(port=0)
    if not getattr(creds, "id_token", None):
        raise RuntimeError("Failed to obtain ID token from Google.")
    return creds.id_token


def main():
    print("Starting Google Desktop OAuth flow…")
    id_token = get_id_token_via_desktop_flow()
    # Show token audience and what backend likely expects
    try:
        info = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=10,
        ).json()
        print("Token aud:", info.get("aud"), " email:", info.get("email"))
        print("Backend allowed GOOGLE_CLIENT_ID(S):", ALLOWED_GOOGLE_IDS)
    except Exception:
        pass
    print("ID token acquired. Calling /auth/login …")

    login_payload = {
        "provider": "google",
        "token": id_token,
        "device_info": {"platform": "desktop", "source": "tester"},
    }
    r = requests.post(
        f"{BACKEND_BASE_URL}/auth/login",
        json=login_payload,
        timeout=20,
    )
    print("/auth/login status:", r.status_code)
    print(r.text)

    data = r.json()
    if data.get("success") and data.get("session_token"):
        session_token = data["session_token"]
        print("Session token:", session_token)
        prof = requests.get(
            f"{BACKEND_BASE_URL}/auth/profile",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=10,
        )
        print("/auth/profile status:", prof.status_code)
        print(prof.text)
        return

    if data.get("requires_registration"):
        # Minimal token info decode via tokeninfo
        info = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=10,
        ).json()
        google_sub = info.get("sub")
        first_name = info.get("given_name", "")
        last_name = info.get("family_name", "")
        email = info.get("email", "")

        print("Registration required. Enter birthdate (YYYY-MM-DD), must be 13+:")
        bdate_str = input("> ").strip()
        try:
            y, m, d = map(int, bdate_str.split("-"))
            _ = date(y, m, d)
        except Exception:
            print("Invalid date format.")
            return

        reg_payload = {
            "provider": "google",
            "provider_user_id": google_sub,
            "first_name": first_name or "",
            "last_name": last_name or "",
            "email": email or "",
            "birthdate": bdate_str,
        }
        rr = requests.post(
            f"{BACKEND_BASE_URL}/auth/register",
            json=reg_payload,
            timeout=20,
        )
        print("/auth/register status:", rr.status_code)
        print(rr.text)
        if rr.ok:
            try:
                out = rr.json()
                session_token = out.get("session_token")
                if session_token:
                    prof = requests.get(
                        f"{BACKEND_BASE_URL}/auth/profile",
                        headers={"Authorization": f"Bearer {session_token}"},
                        timeout=10,
                    )
                    print("/auth/profile status:", prof.status_code)
                    print(prof.text)
            except Exception:
                pass


if __name__ == "__main__":
    main()


