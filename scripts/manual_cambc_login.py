"""Complete cambc login manually from the browser callback URL.

This works around remote-editor setups where `cambc login` listens on
127.0.0.1 inside the remote machine, but the browser runs locally and cannot
reach that callback server.

Usage:

    uv run python scripts/manual_cambc_login.py \
      "http://127.0.0.1:39169/callback?code=...&state=..."

You can also pass just the code:

    uv run python scripts/manual_cambc_login.py --code "..."
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlparse


DEFAULT_API_URL = "https://game.battlecode.cam"
CREDENTIALS_DIR = Path.home() / ".cambc"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exchange a Battlecode CLI auth code and save cambc credentials."
    )
    parser.add_argument(
        "callback_url",
        nargs="?",
        help="Full failed localhost callback URL containing ?code=...",
    )
    parser.add_argument(
        "--code",
        help="Authorization code from the callback URL. Overrides callback_url parsing.",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("CAMBC_API_URL", DEFAULT_API_URL),
        help=f"Battlecode API base URL. Defaults to {DEFAULT_API_URL}.",
    )
    return parser.parse_args()


def extract_code(callback_url: str) -> str:
    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)
    code = params.get("code", [None])[0]
    if not code:
        raise ValueError("No code parameter found in callback URL.")
    return code


def exchange_code(api_url: str, code: str) -> dict:
    payload = json.dumps({"code": code}).encode()
    req = urllib.request.Request(
        f"{api_url.rstrip('/')}/api/cli/exchange",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def save_credentials(data: dict) -> None:
    token = data.get("token")
    if not token:
        raise ValueError("Exchange response did not include a token.")

    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_FILE.write_text(
        json.dumps(
            {
                "token": token,
                "expires_at": data.get("expires_at", ""),
                "user": data.get("user", {}),
                "team": data.get("team"),
            },
            indent=2,
        )
    )
    CREDENTIALS_FILE.chmod(0o600)


def main() -> int:
    args = parse_args()

    code = args.code
    if not code and args.callback_url:
        code = extract_code(args.callback_url)
    if not code:
        print("Provide either a callback URL or --code.", file=sys.stderr)
        return 2

    try:
        data = exchange_code(args.api_url, code)
        save_credentials(data)
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read())
            message = body.get("error", str(exc))
        except Exception:
            message = str(exc)
        print(f"Authentication failed: {message}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
        return 1

    user = data.get("user", {})
    team = data.get("team")

    print(f"Saved credentials to {CREDENTIALS_FILE}")
    print(f"User: {user.get('name', '?')} ({user.get('email', '?')})")
    if team:
        print(f"Team: {team.get('name', '?')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
