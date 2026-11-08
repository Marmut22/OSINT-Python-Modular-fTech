
from core.banner import show_banner
from modules.username import check_username, save_report
from modules.report import analyze_report


def main():
    show_banner()

    while True:
        print("\n[ MAIN MENU ]")
        print("[1] Username Intelligence")
        print("[2] Domain Intelligence")
        print("[3] Email Intelligence")
        print("[4] IP Intelligence")
        print("[5] JSON Report Analyzer")
        print("[0] Exit")

        choice = input("\nfTech > ").strip()

        if choice == "1":
            username = input(
                "\nEnter authorized username > "
            ).strip()

            try:
                data = check_username(username)

                if data:
                    save_report(data)

            except (ValueError, FileNotFoundError) as error:
                print(f"\n[!] Configuration error: {error}")

            except Exception as error:
                print(f"\n[!] Error: {error}")

        elif choice == "2":
            print("\n[+] Domain Intelligence - Coming soon")

        elif choice == "3":
            print("\n[+] Email Intelligence - Coming soon")

        elif choice == "4":
            print("\n[+] IP Intelligence - Coming soon")

        elif choice == "5":
            analyze_report()

        elif choice == "0":
            print("\n[*] Exiting fTech...")
            break

        else:
            print("\n[!] Invalid option")


if __name__ == "__main__":
    main()
