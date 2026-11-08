
import json
import re
import time
import ipaddress

from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit


BASE_DIR = Path(__file__).resolve().parent.parent
PLATFORM_FILE = BASE_DIR / "config" / "platforms.json"
OUTPUT_DIR = BASE_DIR / "output"

REQUEST_DELAY = 2
REQUEST_TIMEOUT = 8
MAX_PLATFORMS = 100


def validate_username(username):
    if not username:
        raise ValueError("Username cannot be empty.")

    if len(username) > 64:
        raise ValueError("Username is too long.")

    if not re.fullmatch(r"[A-Za-z0-9._-]+", username):
        raise ValueError(
            "Use only letters, numbers, dots, underscores, and hyphens."
        )

    return username


def valid_platform_url(url):
    if not isinstance(url, str):
        return False

    if url.count("{username}") != 1:
        return False

    if any(char in url for char in "\r\n\t"):
        return False

    try:
        parsed = urlsplit(url)

        if parsed.scheme != "https":
            return False

        hostname = parsed.hostname

        if not hostname or "." not in hostname:
            return False

        if hostname.lower() == "localhost":
            return False

        try:
            ipaddress.ip_address(hostname)
            return False
        except ValueError:
            pass

        return True

    except ValueError:
        return False


def load_platforms():
    if not PLATFORM_FILE.exists():
        raise FileNotFoundError(
            f"Platform configuration not found: {PLATFORM_FILE}"
        )

    with PLATFORM_FILE.open("r", encoding="utf-8") as file:
        config = json.load(file)

    platforms = config.get("platforms", [])

    if not isinstance(platforms, list):
        raise ValueError("The platforms field must be a list.")

    if len(platforms) > MAX_PLATFORMS:
        raise ValueError(
            f"Maximum platform limit is {MAX_PLATFORMS}."
        )

    valid_platforms = []
    seen_names = set()

    for platform in platforms:
        if not isinstance(platform, dict):
            continue

        name = platform.get("name")
        category = platform.get("category", "Other")
        url = platform.get("url")

        if not isinstance(name, str) or not name.strip():
            continue

        if name in seen_names:
            continue

        if not isinstance(category, str):
            continue

        if not valid_platform_url(url):
            print(f"[!] Skipping invalid platform: {name}")
            continue

        seen_names.add(name)

        valid_platforms.append({
            "name": name.strip(),
            "category": category.strip(),
            "url": url
        })

    return valid_platforms


def check_profile(platform, username):
    encoded_username = quote(username, safe="._-")
    profile_url = platform["url"].replace(
        "{username}", encoded_username
    )

    request = Request(
        profile_url,
        headers={
            "User-Agent": "fTech-OSINT-Lab/0.3",
            "Accept": "text/html"
        }
    )

    try:
        with urlopen(
            request,
            timeout=REQUEST_TIMEOUT
        ) as response:

            if response.status == 200:
                status = "POSSIBLY FOUND"
            else:
                status = "UNKNOWN"

    except HTTPError as error:
        if error.code == 404:
            status = "NOT FOUND"
        elif error.code == 429:
            status = "RATE LIMITED"
        else:
            status = "UNKNOWN"

    except (URLError, TimeoutError, OSError):
        status = "CONNECTION ERROR"

    except Exception:
        status = "UNKNOWN"

    return {
        "platform": platform["name"],
        "category": platform["category"],
        "url": profile_url,
        "status": status
    }


def check_username(username):
    validate_username(username)

    platforms = load_platforms()

    if not platforms:
        print("[!] No valid platforms configured.")
        return None

    results = []

    print("\n" + "=" * 48)
    print("           fTech USERNAME INTELLIGENCE")
    print("=" * 48)

    print(f"[*] Username : {username}")
    print(f"[*] Platforms: {len(platforms)}")
    print(f"[*] Delay    : {REQUEST_DELAY} seconds")
    print("=" * 48)

    for index, platform in enumerate(platforms):

        result = check_profile(platform, username)
        results.append(result)

        print(
            f"[{result['status']}] "
            f"{result['platform']} ({result['category']})"
        )

        if result["status"] == "RATE LIMITED":
            print("[!] Rate limit detected. Stopping scan.")
            break

        if index < len(platforms) - 1:
            time.sleep(REQUEST_DELAY)

    return {
        "tool": "fTech OSINT Toolkit",
        "module": "Username Intelligence",
        "version": "0.3",
        "username": username,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "total_checked": len(results),
        "results": results,
        "limitations": (
            "HTTP responses are preliminary indicators only. "
            "They do not prove account ownership or identity."
        )
    }


def save_report(data):
    if not data:
        print("[!] No report data to save.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filename = OUTPUT_DIR / f"username_{data['username']}.json"

    with filename.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"\n[+] Report saved: {filename}")
