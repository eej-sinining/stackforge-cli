from importlib.resources import files

import pytest

from stackforge import templating
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


FEATURE_TEMPLATE = """start
{% if s3 %}
s3 line __PROJECT__
  {% if cache %}
s3 and cache line
  {% endif %}
{% endif %}
end
"""


def _render_feature_template(monkeypatch, features):
    class FakeResource:
        def read_text(self, encoding):
            return FEATURE_TEMPLATE

    monkeypatch.setattr(templating, "_template_resource", lambda engine, path: FakeResource())
    return render_text("dotnet", "x.txt", "MyApi", features)


def test_feature_blocks_are_dropped_when_disabled(monkeypatch):
    assert _render_feature_template(monkeypatch, frozenset()) == "start\nend\n"


def test_feature_blocks_are_kept_when_enabled_and_markers_removed(monkeypatch):
    assert _render_feature_template(monkeypatch, frozenset({"s3"})) == "start\ns3 line MyApi\nend\n"
    assert _render_feature_template(monkeypatch, frozenset({"s3", "cache"})) == (
        "start\ns3 line MyApi\ns3 and cache line\nend\n"
    )


@pytest.mark.parametrize("content", ["{% if s3 %}\nx\n", "x\n{% endif %}\n"])
def test_unbalanced_feature_blocks_raise(content):
    with pytest.raises(ValueError, match="x.txt"):
        templating._apply_features(content, frozenset(), "x.txt")
