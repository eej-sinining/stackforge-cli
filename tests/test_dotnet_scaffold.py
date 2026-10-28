import json
import shutil
import subprocess
from importlib.resources import files

import pytest

from conftest import PROJECT, git
from stackforge.templating import PROJECT_LOWER_TOKEN, PROJECT_TOKEN

LAYERS = ["API", "Application", "Domain", "Infrastructure", "Persistence"]

S3_ONLY_FILES = {
    "Application/Interfaces/IFileStorageService.cs",
    "Application/Features/Files/FileKeys.cs",
    "Application/Features/Files/Commands/UploadFile/UploadFileCommand.cs",
    "Application/Features/Files/Commands/UploadFile/UploadFileCommandHandler.cs",
    "Application/Features/Files/Commands/UploadFile/UploadFileCommandValidator.cs",
    "Application/Features/Files/Queries/GetFileUrl/GetFileUrlQuery.cs",
    "Application/Features/Files/Queries/GetFileUrl/GetFileUrlQueryHandler.cs",
    "Infrastructure/Options/S3Options.cs",
    "Infrastructure/Services/S3StorageService.cs",
}


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


def test_every_template_is_generated(scaffolded_s3):
    # The S3 variant enables every optional feature, so it renders every template.
    generated = _generated_files(scaffolded_s3)

    missing = _bundled_template_outputs() - generated
    assert not missing, f"templates never rendered: {sorted(missing)}"


def test_default_template_has_no_s3_components(scaffolded):
    generated = _generated_files(scaffolded)

    assert not S3_ONLY_FILES & generated
    for path in generated:
        text = (scaffolded / path).read_text()
        for marker in ("S3", "AWS", "IFileStorageService"):
            assert marker not in text, f"{marker} in {path}"


def test_s3_template_generates_s3_components(scaffolded_s3):
    assert S3_ONLY_FILES <= _generated_files(scaffolded_s3)

    infrastructure_csproj = (scaffolded_s3 / "Infrastructure/Infrastructure.csproj").read_text()
    application_csproj = (scaffolded_s3 / "Application/Application.csproj").read_text()
    assert 'Include="AWSSDK.S3"' in infrastructure_csproj
    # Clean Architecture: Application only sees the abstraction, never the AWS SDK.
    assert "AWSSDK" not in application_csproj
    for path in _generated_files(scaffolded_s3):
        if path.startswith("Application/"):
            assert "Amazon" not in (scaffolded_s3 / path).read_text(), path

    configure = (scaffolded_s3 / "Infrastructure/ConfigureServices.cs").read_text()
    assert "services.AddScoped<IFileStorageService, S3StorageService>();" in configure
    assert ".BindConfiguration(S3Options.SectionName)" in configure


@pytest.mark.parametrize("settings", ["API/appsettings.json", "API/appsettings.Development.json"])
def test_s3_settings_are_valid_json_without_credentials(scaffolded, scaffolded_s3, settings):
    plain = json.loads((scaffolded / settings).read_text())
    s3 = json.loads((scaffolded_s3 / settings).read_text())

    assert "S3" not in plain
    assert s3["S3"]["BucketName"] == f"{PROJECT.lower()}-files"
    assert s3["S3"]["Region"]
    serialized = json.dumps(s3["S3"]).lower()
    assert "secret" not in serialized and "accesskey" not in serialized


def test_s3_credentials_come_from_environment(scaffolded_s3):
    env = (scaffolded_s3 / ".env").read_text()
    compose = (scaffolded_s3 / "docker-compose.yml").read_text()

    assert "AWS_ACCESS_KEY_ID=\n" in env
    assert "AWS_SECRET_ACCESS_KEY=\n" in env
    assert "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}" in compose


def test_unknown_feature_is_rejected(tmp_path):
    from stackforge.engines.dotnet.scaffolder import scaffold_folders

    with pytest.raises(ValueError, match="redis"):
        scaffold_folders(tmp_path, PROJECT, frozenset({"redis"}))


def test_generates_project_and_solution_files(scaffolded):
    for layer in LAYERS:
        assert (scaffolded / layer / f"{layer}.csproj").is_file()
    assert (scaffolded / f"{PROJECT}.sln").is_file()


@pytest.mark.parametrize("variant", ["scaffolded", "scaffolded_s3"])
def test_no_placeholder_is_left_behind(variant, request):
    base = request.getfixturevalue(variant)
    for path in _generated_files(base):
        text = (base / path).read_text()
        assert PROJECT_TOKEN not in text, path
        assert PROJECT_LOWER_TOKEN not in text, path
        assert "{%" not in text, path


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
@pytest.mark.parametrize("variant", ["scaffolded", "scaffolded_s3"])
def test_generated_solution_builds(variant, request):
    base = request.getfixturevalue(variant)
    result = subprocess.run(
        ["dotnet", "build", f"{PROJECT}.sln", "-nologo"],
        cwd=base,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-2000:]
    assert " 0 Error(s)" in result.stdout
