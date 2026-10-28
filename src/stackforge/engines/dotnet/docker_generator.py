from pathlib import Path
from stackforge import ui
from stackforge.templating import render_file

ENGINE = "dotnet"


def generate_dockerfile(base: Path, project: str = ""):
    render_file(ENGINE, base, "Dockerfile", project)
    ui.file_created("Dockerfile")


def generate_docker_compose(base: Path, project: str):
    render_file(ENGINE, base, "docker-compose.yml", project)
    ui.file_created("docker-compose.yml")
