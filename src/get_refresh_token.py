"""
Helper script to obtain a Strava refresh token via OAuth.

Run this script once to generate your STRAVA_REFRESH_TOKEN.
Requires STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET to be set in your .env file.
"""

import http.server
import os
import threading
import urllib.parse
import webbrowser

import requests
from dotenv import load_dotenv

_PORT = 8080
_REDIRECT_URI = f"http://localhost:{_PORT}"


def main() -> None:
    load_dotenv()

    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in your .env file.")
        return

    auth_url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        "&response_type=code"
        f"&redirect_uri={_REDIRECT_URI}"
        "&approval_prompt=force"
        "&scope=activity:read_all"
    )

    auth_code: str | None = None
    code_received = threading.Event()

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            nonlocal auth_code
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            auth_code = params.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<p>Authorization complete. You can close this tab.</p>")
            code_received.set()

        def log_message(self, format: str, *args: object) -> None:
            pass

    server = http.server.HTTPServer(("localhost", _PORT), _Handler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    print("Opening Strava authorization page in your browser...")
    webbrowser.open(auth_url)
    print("Waiting for authorization...")

    code_received.wait()
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
    )

    if not response.ok:
        print(f"Error: token exchange failed (HTTP {response.status_code}).")
        return

    refresh_token = response.json().get("refresh_token")
    print(f"\nYour refresh token:\n\n  STRAVA_REFRESH_TOKEN={refresh_token}\n")
    print("Copy this value into your .env file or GitHub secrets.")


if __name__ == "__main__":
    main()
