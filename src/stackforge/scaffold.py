from pathlib import Path
from stackforge.engines.dotnet.scaffolder import scaffold_folders
from colorama import init, Fore, Style
import re

init(autoreset=True)

def is_valid_project_name(name: str) -> bool:
    return bool(re.match(r'^[A-Za-z][A-Za-z0-9]*$', name))


def select_framework() -> str:
    print(f"  {Fore.CYAN}Select a framework:{Style.RESET_ALL}\n")
    print(f"    {Fore.GREEN}1.{Style.RESET_ALL} .NET Clean Architecture (CQRS)")
    print(f"    {Fore.YELLOW}2.{Style.RESET_ALL} Django                          [coming soon]")
    print(f"    {Fore.YELLOW}3.{Style.RESET_ALL} FastAPI                         [coming soon]")
    print(f"    {Fore.YELLOW}4.{Style.RESET_ALL} Flask                           [coming soon]")
    print(f"    {Fore.RED}5.{Style.RESET_ALL} exit")

    choice = input(f"\n  {Fore.CYAN}Choice [n]:{Style.RESET_ALL} ").strip() or "1"
    return choice


def main():
    print(Fore.CYAN + r"""
  _____ _             _    ______
 / ____| |           | |  |  ____|
| (___ | |_ __ _  ___| | _| |__ ___  _ __ __ _  ___
 \___ \| __/ _` |/ __| |/ /  __/ _ \| '__/ _` |/ _ \
 ____) | || (_| | (__|   <| | | (_) | | | (_| |  __/
|_____/ \__\__,_|\___|_|\_\_|  \___/|_|  \__, |\___|
                                           __/ |
                                          |___/
""" + Style.RESET_ALL + f"  {Fore.WHITE}.NET Clean Architecture Scaffolder{Style.RESET_ALL}\n")

    while True:
        framework = select_framework()

        if framework == "5":
            print(f"\n  {Fore.YELLOW}Exiting...{Style.RESET_ALL}")
            break

        if framework != "1":
            print(f"\n  {Fore.YELLOW}[!] This framework is under development. Stay tuned!{Style.RESET_ALL}\n")
            continue

        project_name = input(f"\n  {Fore.CYAN}Enter project name (PascalCase, no spaces):{Style.RESET_ALL} ").strip()

        if not project_name:
            print(f"  {Fore.RED}[!] Project name cannot be empty.{Style.RESET_ALL}\n")
            continue

        if not is_valid_project_name(project_name):
            print(f"  {Fore.RED}[!] Project name must start with a letter and contain only letters and numbers.")
            print(f"      Example: RaiderXpress, MyApi, StackForge{Style.RESET_ALL}\n")
            continue

        base_path = Path.home() / "stackforge" / project_name

        if base_path.exists():
            print(f"\n  {Fore.RED}[!] Project '{project_name}' already exists in the stackforge workspace.")
            print(f"      Path: {base_path}{Style.RESET_ALL}")
            print("      Choose a different project name or delete the existing one.\n")
            continue

        base_path.mkdir(parents=True, exist_ok=True)
        scaffold_folders(base_path, project_name)

        print(f"""
  {Fore.GREEN}✔ Project '{project_name}' created successfully!
  ✔ Location: {base_path}{Style.RESET_ALL}

  {Fore.CYAN}Next steps:{Style.RESET_ALL}
    1. Open the project in Visual Studio or VS Code
    2. Run: docker-compose up --build
    3. Visit: http://localhost:5000/swagger

  Press Ctrl+C to exit or continue to scaffold another project.
        """)


if __name__ == "__main__":
    main()