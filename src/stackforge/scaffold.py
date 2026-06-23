from pathlib import Path
from stackforge.engines.dotnet.scaffolder import scaffold_folders
from stackforge.version import get_installed_version, notify_if_update_available
from stackforge.project_name import is_valid_project_name, to_pascal_case
from stackforge import ui
import sys


FRAMEWORK_CHOICES = frozenset({"dotnet", "django", "fastapi", "flask", "exit"})


def select_framework() -> str:
    ui.info("\n  Select a framework:\n")
    ui.menu_item("dotnet", ".NET Clean Architecture (CQRS)")
    ui.menu_item("django", "Django                          [coming soon]", style=ui.Fore.YELLOW)
    ui.menu_item("fastapi", "FastAPI                         [coming soon]", style=ui.Fore.YELLOW)
    ui.menu_item("flask", "Flask                           [coming soon]", style=ui.Fore.YELLOW)
    ui.menu_item("exit", "Exit", style=ui.Fore.RED)

    choice = ui.prompt("\n  Framework [dotnet]:").lower() or "dotnet"
    if choice not in FRAMEWORK_CHOICES:
        ui.error(f"Unknown framework '{choice}'.")
        ui.step("Options: dotnet, django, fastapi, flask, exit\n")
        return ""
    return choice


def main():
    if "--version" in sys.argv or "-V" in sys.argv:
        print(get_installed_version())
        return

    notify_if_update_available()
    ui.banner(".NET Clean Architecture Scaffolder", get_installed_version())
    print()

    while True:
        framework = select_framework()

        if not framework:
            continue

        if framework == "exit":
            ui.warn("\n  Exiting...")
            break

        if framework != "dotnet":
            ui.warn("\n  This framework is under development. Stay tuned!\n")
            continue

        raw_name = ui.prompt(
            "\n  Enter project name (PascalCase, camelCase, snake_case, or kebab-case):"
        )

        if not raw_name:
            ui.error("Project name cannot be empty.\n")
            continue

        if not is_valid_project_name(raw_name):
            ui.error("Invalid project name. Use letters, numbers, hyphens, or underscores.")
            ui.step("Examples: MyApi, myApi, my_api, my-api\n")
            continue

        project_name = to_pascal_case(raw_name)
        if project_name != raw_name:
            ui.info(f"  Normalized to: {project_name}")

        base_path = Path.home() / "stackforge" / project_name

        if base_path.exists():
            ui.error(f"\n  Project '{project_name}' already exists in the stackforge workspace.")
            ui.step(f"Path: {base_path}")
            ui.step("Choose a different project name or delete the existing one.\n")
            continue

        base_path.mkdir(parents=True, exist_ok=True)
        scaffold_folders(base_path, project_name)

        ui.section("Project ready")
        ui.success(f"Created '{project_name}'")
        ui.success(f"Location: {base_path}")
        ui.info("\n  Next steps:")
        ui.step("Open the project in Visual Studio or VS Code")
        ui.step("Run: docker-compose up --build")
        ui.step("Visit: http://localhost:5000/swagger")
        ui.muted("\n  Press Ctrl+C to exit or continue to scaffold another project.\n")


if __name__ == "__main__":
    main()
