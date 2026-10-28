from pathlib import Path
from stackforge import ui
from stackforge.templating import render_file

ENGINE = "dotnet"


def generate_env(base: Path, project: str):
    render_file(ENGINE, base, ".env", project)
    ui.file_created(".env")


def generate_appsettings(base: Path, project: str):
    render_file(ENGINE, base, "API/appsettings.json", project)
    ui.file_created("API/appsettings.json")


def generate_appsettings_development(base: Path, project: str):
    render_file(ENGINE, base, "API/appsettings.Development.json", project)
    ui.file_created("API/appsettings.Development.json")
