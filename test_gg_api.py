import os
import sys

import requests
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*_args, **_kwargs):
        return False


def main() -> int:
    load_dotenv()

    api_key = os.getenv("GGDEALS_API_KEY")
    region = (os.getenv("GGDEALS_REGION") or "us").lower()

    if not api_key:
        print("Missing GGDEALS_API_KEY in .env")
        return 1

    url = "https://api.gg.deals/v1/prices/by-steam-app-id/"
    params = {
        "key": api_key,
        "ids": "1,420",
        "region": region,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        print(response.text[:500])
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
