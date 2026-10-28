from pathlib import Path
from stackforge import ui
from . import features as feature_flags
from .csproj_generator import generate_csproj
from .program_generator import generate_configure_services, generate_program_cs
from .docker_generator import generate_dockerfile, generate_docker_compose
from .config_generator import generate_env, generate_appsettings, generate_appsettings_development
from .git_generator import generate_gitignore, generate_github_workflow, generate_sln, git_init
from .api_generator import generate_api_structure
from .layers_generator import (
    generate_application_layer,
    generate_domain_layer,
    generate_infrastructure_layer,
    generate_persistence_layer,
)

def scaffold_folders(base: Path, project: str, features: frozenset[str] = frozenset()):
    """Generates the .NET solution into ``base``; ``features`` holds optional extras from ``features.ALL``."""
    unknown = features - feature_flags.ALL
    if unknown:
        raise ValueError(f"Unknown .NET template features: {sorted(unknown)}")

    layers = [
        "API",
        "Application",
        "Domain",
        "Infrastructure",
        "Persistence"
    ]

    ui.section(f"Scaffolding '{project}'")

    ui.step("Creating folders")
    for layer in layers:
        folder = base / layer
        folder.mkdir(parents=True, exist_ok=True)
        ui.file_created(layer)

    ui.section("Generating .csproj files")
    for layer in layers:
        generate_csproj(layer, base, features)

    ui.section("Generating service registrations")
    for layer in ["Application", "Infrastructure", "Persistence", "API"]:
        generate_configure_services(layer, base, project, features)

    ui.section("Generating Program.cs")
    generate_program_cs(base, project)

    ui.section("Generating Docker files")
    generate_dockerfile(base)
    generate_docker_compose(base, project, features)

    ui.section("Generating config files")
    generate_env(base, project, features)
    generate_appsettings(base, project, features)
    generate_appsettings_development(base, project, features)

    ui.section("Generating API layer")
    generate_api_structure(base, project)

    ui.section("Generating layer files")
    generate_application_layer(base, project, features)
    generate_domain_layer(base, project)
    generate_infrastructure_layer(base, project, features)
    generate_persistence_layer(base, project)

    ui.section("Generating solution file")
    generate_sln(base, project)

    ui.section("Generating .gitignore")
    generate_gitignore(base)

    ui.section("Generating GitHub workflow")
    generate_github_workflow(base)

    ui.section("Initializing Git repository")
    git_init(base, project)

    ui.done()
