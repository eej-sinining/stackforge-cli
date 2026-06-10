from pathlib import Path
from .csproj_generator import generate_csproj
from .program_generator import generate_configure_services, generate_program_cs
from .docker_generator import generate_dockerfile, generate_docker_compose
from .config_generator import generate_env, generate_appsettings, generate_appsettings_development
from .git_generator import generate_gitignore, generate_sln, git_init
from .api_generator import generate_api_structure
from .layers_generator import (
    generate_application_layer,
    generate_domain_layer,
    generate_infrastructure_layer,
    generate_persistence_layer,
)

def scaffold_folders(base: Path, project: str):
    layers = [
        "API",
        "Application",
        "Domain",
        "Infrastructure",
        "Persistence"
    ]

    print(f"\nScaffolding folders for project '{project}'...")

    for layer in layers:
        folder = base / layer
        folder.mkdir(parents=True, exist_ok=True)
        print(f"    [+] {layer}")

    print("\nFolder structure created.")

    print("\nGenerating .csproj files...")
    for layer in layers:
        generate_csproj(layer, base)

    print("\nGenerating service registrations...")
    for layer in ["Application", "Infrastructure", "Persistence"]:
        generate_configure_services(layer, base, project)

    print("\nGenerating Program.cs...")
    generate_program_cs(base, project)

    print("\nGenerating Docker files...")
    generate_dockerfile(base)
    generate_docker_compose(base, project)

    print("\nGenerating config files...")
    generate_env(base, project)
    generate_appsettings(base, project)
    generate_appsettings_development(base, project)

    print("\nGenerating API layer...")
    generate_api_structure(base, project)

    print("\nGenerating layer files...")
    generate_application_layer(base, project)
    generate_domain_layer(base, project)
    generate_infrastructure_layer(base, project)
    generate_persistence_layer(base, project)

    print("\nGenerating solution file...")
    generate_sln(base, project)

    print("\nGenerating .gitignore...")
    generate_gitignore(base)

    print("\nInitializing Git repository...")
    git_init(base, project)

    print("\nDone.")