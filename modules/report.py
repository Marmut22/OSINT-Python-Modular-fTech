
import json
from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def list_reports():
    OUTPUT_DIR.mkdir(exist_ok=True)

    reports = sorted(
        OUTPUT_DIR.glob("username_*.json"),
        key=lambda file: file.stat().st_mtime,
        reverse=True
    )

    return reports


def analyze_report():
    reports = list_reports()

    if not reports:
        print("\n[!] No reports found.")
        return

    print("\n[ AVAILABLE REPORTS ]")

    for index, report in enumerate(reports, start=1):
        print(f"[{index}] {report.name}")

    print("[0] Back")

    choice = input("\nSelect report > ").strip()

    if choice == "0":
        return

    if not choice.isdigit():
        print("[!] Invalid selection.")
        return

    index = int(choice) - 1

    if index < 0 or index >= len(reports):
        print("[!] Report not found.")
        return

    selected_file = reports[index]

    try:
        with selected_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except (OSError, json.JSONDecodeError) as error:
        print(f"\n[!] Cannot read report: {error}")
        return

    results = data.get("results", [])

    if not isinstance(results, list):
        print("\n[!] Invalid report structure.")
        return

    print("\n" + "=" * 45)
    print("             fTech REPORT ANALYZER")
    print("=" * 45)

    print(f"Username    : {data.get('username', 'Unknown')}")
    print(f"Checked at  : {data.get('checked_at', 'Unknown')}")
    print(f"Total checks: {len(results)}")

    print("\n[ PLATFORM RESULTS ]")

    counts = {}

    for result in results:
        if not isinstance(result, dict):
            continue

        platform = result.get("platform", "Unknown")
        status = result.get("status", "UNKNOWN")
        url = result.get("url", "N/A")

        counts[status] = counts.get(status, 0) + 1

        print(f"\nPlatform : {platform}")
        print(f"Status   : {status}")
        print(f"URL      : {url}")

    print("\n[ SUMMARY ]")

    for status, count in sorted(counts.items()):
        print(f"{status}: {count}")

    print("\n" + "=" * 45)
    print("[+] Analysis completed.")
