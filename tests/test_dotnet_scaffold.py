import shutil
import subprocess
from importlib.resources import files

import pytest

from conftest import PROJECT, git
from stackforge.templating import PROJECT_LOWER_TOKEN, PROJECT_TOKEN

LAYERS = ["API", "Application", "Domain", "Infrastructure", "Persistence"]


def _bundled_template_outputs() -> set[str]:
    """Output paths of every bundled .NET template (dot_ prefix and .tmpl suffix undone)."""
    root = files("stackforge").joinpath("templates", "dotnet")
    outputs = set()

    def walk(node, parts):
        for child in node.iterdir():
            name = "." + child.name[4:] if child.name.startswith("dot_") else child.name
            if child.is_dir():
                walk(child, parts + [name])
            else:
                outputs.add("/".join(parts + [name.removesuffix(".tmpl")]))

    walk(root, [])
    return outputs


def _generated_files(base):
    return {p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file() and ".git/" not in p.as_posix()}


def test_every_template_is_generated(scaffolded):
    generated = _generated_files(scaffolded)

    missing = _bundled_template_outputs() - generated
    assert not missing, f"templates never rendered: {sorted(missing)}"


def test_generates_project_and_solution_files(scaffolded):
    for layer in LAYERS:
        assert (scaffolded / layer / f"{layer}.csproj").is_file()
    assert (scaffolded / f"{PROJECT}.sln").is_file()


def test_no_placeholder_is_left_behind(scaffolded):
    for path in _generated_files(scaffolded):
        text = (scaffolded / path).read_text()
        assert PROJECT_TOKEN not in text, path
        assert PROJECT_LOWER_TOKEN not in text, path


def test_project_name_is_substituted(scaffolded):
    program = (scaffolded / "API/Program.cs").read_text()
    compose = (scaffolded / "docker-compose.yml").read_text()

    assert f"using {PROJECT}.API;" in program
    assert f"{PROJECT.lower()}_db" in compose


def test_solution_lists_all_layers_with_build_configurations(scaffolded):
    sln = (scaffolded / f"{PROJECT}.sln").read_text()

    for layer in LAYERS:
        assert f'"{layer}\\{layer}.csproj"' in sln
    assert "GlobalSection(ProjectConfigurationPlatforms)" in sln
    assert sln.count(".Debug|Any CPU.Build.0") == len(LAYERS)


def test_api_configure_services_holds_cors_and_deny_by_default(scaffolded):
    configure = (scaffolded / "API/ConfigureServices.cs").read_text()
    program = (scaffolded / "API/Program.cs").read_text()
    account = (scaffolded / "API/Controllers/Main/AccountController.cs").read_text()

    assert "AddApiServices" in configure
    assert ".WithOrigins(" in configure
    assert "FallbackPolicy" in configure
    assert "builder.Services.AddApiServices(builder.Configuration);" in program
    assert f"app.UseCors({PROJECT}.API.ConfigureServices.CorsPolicy);" in program
    # Deny-by-default would otherwise block login.
    assert '[AllowAnonymous]\n        [HttpPost("login")]' in account


def test_git_repository_has_main_and_environment_branches(scaffolded_with_git):
    branches = git(scaffolded_with_git, "branch", "--format=%(refname:short)").split()

    assert sorted(branches) == ["development", "main", "staging"]
    assert git(scaffolded_with_git, "branch", "--show-current").strip() == "main"
    assert git(scaffolded_with_git, "status", "--porcelain") == ""


@pytest.mark.dotnet
@pytest.mark.skipif(shutil.which("dotnet") is None, reason="dotnet SDK is not installed")
def test_generated_solution_builds(scaffolded):
    result = subprocess.run(
        ["dotnet", "build", f"{PROJECT}.sln", "-nologo"],
        cwd=scaffolded,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-2000:]
    assert " 0 Error(s)" in result.stdout
