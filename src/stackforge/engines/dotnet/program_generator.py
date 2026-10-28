from pathlib import Path
from stackforge import ui
from stackforge.templating import render_file

ENGINE = "dotnet"

# Layers that get a ConfigureServices.Add<Layer>Services() extension.
CONFIGURE_SERVICES_LAYERS = {"Application", "Infrastructure", "Persistence", "API"}


def generate_configure_services(layer: str, base: Path, project: str, features: frozenset[str] = frozenset()):
    if layer not in CONFIGURE_SERVICES_LAYERS:
        return

    render_file(ENGINE, base, f"{layer}/ConfigureServices.cs", project, features)
    ui.file_created(f"{layer}/ConfigureServices.cs")


def generate_program_cs(base: Path, project: str):
    render_file(ENGINE, base, "API/Program.cs", project)
    ui.file_created("API/Program.cs")
