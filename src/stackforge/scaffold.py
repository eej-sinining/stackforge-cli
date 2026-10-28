from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from stackforge.engines.dotnet import features as dotnet_features
from stackforge.engines.dotnet.scaffolder import scaffold_folders
from stackforge.version import get_installed_version, notify_if_update_available
from stackforge.project_name import is_valid_project_name, to_pascal_case
from stackforge import ui
import sys


@dataclass(frozen=True)
class Framework:
    """A menu entry backed by an engine. Add new frameworks (e.g. Next.js) to ``FRAMEWORKS``."""

    label: str
    # Asks the framework-specific questions; returns the enabled template features.
    prompt_features: Callable[[], frozenset[str]]
    scaffold: Callable[[Path, str, frozenset[str]], None]
    next_steps: tuple[str, ...]


EXIT_CHOICE = "exit"

YES_ANSWERS = frozenset({"y", "yes"})
NO_ANSWERS = frozenset({"n", "no"})


def prompt_yes_no(label: str) -> bool:
    """Asks until the user explicitly answers yes or no; there is no default."""
    while True:
        answer = ui.prompt(f"\n  {label} [y/n]:").lower()
        if answer in YES_ANSWERS:
            return True
        if answer in NO_ANSWERS:
            return False
        ui.error("Please answer 'y' or 'n'.")


def prompt_dotnet_features() -> frozenset[str]:
    features = set()
    if prompt_yes_no("Use the S3-ready template (AWS S3 file storage)?"):
        features.add(dotnet_features.S3)
    return frozenset(features)


FRAMEWORKS: dict[str, Framework] = {
    "dotnet": Framework(
        label=".NET Clean Architecture (CQRS)",
        prompt_features=prompt_dotnet_features,
        scaffold=scaffold_folders,
        next_steps=(
            "Open the project in Visual Studio or VS Code",
            "Run: docker-compose up --build",
            "Visit: http://localhost:5000/swagger",
        ),
    ),
}

MENU_CHOICES = (*FRAMEWORKS, EXIT_CHOICE)


def select_framework() -> str:
    """Returns a key of ``FRAMEWORKS``, ``EXIT_CHOICE``, or ``""`` when the input is empty or unknown."""
    ui.info("\n  Select a framework:\n")
    for key, framework in FRAMEWORKS.items():
        ui.menu_item(key, framework.label)
    ui.menu_item(EXIT_CHOICE, "Exit", style=ui.Fore.RED)

    options = ", ".join(MENU_CHOICES)
    choice = ui.prompt(f"\n  Framework ({options}):").lower()
    if not choice:
        ui.error("Please select an option.")
        ui.step(f"Options: {options}\n")
        return ""
    if choice not in MENU_CHOICES:
        ui.error(f"Unknown framework '{choice}'.")
        ui.step(f"Options: {options}\n")
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
        choice = select_framework()

        if not choice:
            continue

        if choice == EXIT_CHOICE:
            ui.warn("\n  Exiting...")
            break

        framework = FRAMEWORKS[choice]
        features = framework.prompt_features()

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
        framework.scaffold(base_path, project_name, features)

        ui.section("Project ready")
        ui.success(f"Created '{project_name}'")
        ui.success(f"Location: {base_path}")
        ui.info("\n  Next steps:")
        for next_step in framework.next_steps:
            ui.step(next_step)
        ui.muted("\n  Press Ctrl+C to exit or continue to scaffold another project.\n")


if __name__ == "__main__":
    main()
