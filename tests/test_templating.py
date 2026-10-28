from importlib.resources import files

from stackforge.templating import PROJECT_LOWER_TOKEN, PROJECT_TOKEN, render_file, render_text


def test_render_text_replaces_both_tokens():
    text = render_text("dotnet", "docker-compose.yml", "MyApi")

    assert "myapi_api" in text
    assert "myapi_db" in text
    assert PROJECT_TOKEN not in text
    assert PROJECT_LOWER_TOKEN not in text


def test_dotfiles_map_to_dot_prefixed_templates(tmp_path):
    render_file("dotnet", tmp_path, ".env", "MyApi")
    render_file("dotnet", tmp_path, ".github/workflows/sync-branches.yml", "MyApi")

    assert "DB_NAME=myapi_db" in (tmp_path / ".env").read_text()
    assert (tmp_path / ".github/workflows/sync-branches.yml").is_file()


def test_templates_are_bundled_with_the_package():
    root = files("stackforge").joinpath("templates", "dotnet")
    templates = [p for p in root.iterdir()]

    assert templates, "no templates found in the installed package"
