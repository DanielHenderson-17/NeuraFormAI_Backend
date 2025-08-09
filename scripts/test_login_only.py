"""
Login-only tester: obtains a Google ID token (Desktop flow) and calls /auth/login,
printing the full backend error detail if any.

Run via: test_login_only.bat
"""

from __future__ import annotations

import os
import requests
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow


load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("ERROR: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set in .env")
    raise SystemExit(1)


def get_id_token() -> str:
    client_config = {
        "installed": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
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


def main():
    id_token = get_id_token()
    try:
        info = requests.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
            timeout=10,
        ).json()
        print("Token aud:", info.get("aud"), " email:", info.get("email"))
    except Exception:
        pass

    r = requests.post(
        f"{BACKEND_BASE_URL}/auth/login",
        json={"provider": "google", "token": id_token, "device_info": {"platform": "desktop", "test": "login_only"}},
        timeout=20,
    )
    print("/auth/login status:", r.status_code)
    print(r.text)


if __name__ == "__main__":
    main()


