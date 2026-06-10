from pathlib import Path
from stackforge.engines.dotnet.scaffolder import scaffold_folders
import re


def is_valid_project_name(name: str) -> bool:
    return bool(re.match(r'^[A-Za-z][A-Za-z0-9]*$', name))


def select_framework() -> str:
    print("  Select a framework:\n")
    print("    1. .NET Clean Architecture (CQRS)")
    print("    2. Django                          [coming soon]")
    print("    3. FastAPI                         [coming soon]")
    print("    4. Flask                           [coming soon]")
    print("    5. exit")

    choice = input("\n  Choice [n]: ").strip() or "1"
    return choice


def main():
    print(r"""
  _____ _             _    ______
 / ____| |           | |  |  ____|
| (___ | |_ __ _  ___| | _| |__ ___  _ __ __ _  ___
 \___ \| __/ _` |/ __| |/ /  __/ _ \| '__/ _` |/ _ \
 ____) | || (_| | (__|   <| | | (_) | | | (_| |  __/
|_____/ \__\__,_|\___|_|\_\_|  \___/|_|  \__, |\___|
                                           __/ |
                                          |___/
  .NET Clean Architecture Scaffolder
    """)

    while True:
        framework = select_framework()

        if framework == "5":
            print("\n  Exiting...")
            break

        if framework != "1":
            print("\n  [!] This framework is under development. Stay tuned!\n")
            continue

        project_name = input("\n  Enter project name (PascalCase, no spaces): ").strip()

        if not project_name:
            print("  [!] Project name cannot be empty.\n")
            continue

        if not is_valid_project_name(project_name):
            print("  [!] Project name must start with a letter and contain only letters and numbers.")
            print("      Example: RaiderXpress, MyApi, StackForge\n")
            continue

        base_path = Path.home() / "stackforge" / project_name

        if base_path.exists():
            print(f"\n  [!] Project '{project_name}' already exists in the stackforge workspace.")
            print(f"      Path: {base_path}")
            print("      Choose a different project name or delete the existing one.\n")
            continue

        base_path.mkdir(parents=True, exist_ok=True)
        scaffold_folders(base_path, project_name)

        print(f"""
  ✔ Project '{project_name}' created successfully!
  ✔ Location: {base_path}

  Next steps:
    1. Open the project in Visual Studio or VS Code
    2. Run: docker-compose up --build
    3. Visit: http://localhost:5000/swagger

  Press Ctrl+C to exit or continue to scaffold another project.
        """)


if __name__ == "__main__":
    main()