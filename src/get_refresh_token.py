"""
Helper script to obtain a Strava refresh token via OAuth.

Run this script once to generate your STRAVA_REFRESH_TOKEN.
Requires STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET to be set in your .env file.
"""

import http.server
import os
import secrets
import threading
import urllib.parse
import webbrowser

import requests
from dotenv import load_dotenv

_PORT = 8080
_REDIRECT_URI = f"http://localhost:{_PORT}"
_AUTH_TIMEOUT = 180


def main() -> None:
    load_dotenv()

    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in your .env file.")
        return

    state = secrets.token_urlsafe(16)
    auth_url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        "&response_type=code"
        f"&redirect_uri={_REDIRECT_URI}"
        "&approval_prompt=force"
        "&scope=activity:read_all"
        f"&state={state}"
    )

    auth_code: str | None = None
    code_received = threading.Event()

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            nonlocal auth_code
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            returned_state = params.get("state", [None])[0]
            if returned_state != state:
                self.send_response(400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<p>Error: invalid state parameter.</p>")
                code_received.set()
                return
            auth_code = params.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<p>Authorization complete. You can close this tab.</p>")
            code_received.set()

        def log_message(self, format: str, *args: object) -> None:
            pass

    try:
        server = http.server.HTTPServer(("localhost", _PORT), _Handler)
    except OSError:
        print(f"Error: port {_PORT} is already in use. Close any other running instance and retry.")
        return

    thread = threading.Thread(target=server.handle_request)
    thread.start()

    print("Opening Strava authorization page in your browser...")
    webbrowser.open(auth_url)
    print(f"Waiting for authorization (timeout: {_AUTH_TIMEOUT}s)...")

    if not code_received.wait(timeout=_AUTH_TIMEOUT):
        server.server_close()
        print("Error: timed out waiting for authorization.")
        return
    thread.join()

    if not auth_code:
        print("Error: no authorization code received.")
        return

    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )

    if not response.ok:
        print(f"Error: token exchange failed (HTTP {response.status_code}).")
        return

    refresh_token = response.json().get("refresh_token")
    print(f"\nYour refresh token:\n\n  STRAVA_REFRESH_TOKEN={refresh_token}\n")
    print("Copy this value into your .env file or GitHub secrets.")


if __name__ == "__main__":
    main()
