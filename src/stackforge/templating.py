"""Renders files from the bundled templates in ``stackforge/templates/<engine>/``.

Template layout mirrors the generated project. Each template file carries a ``.tmpl``
suffix, and a leading ``.`` in a path segment is stored as ``dot_`` (``.env`` ->
``dot_env.tmpl``) so dotfiles survive packaging and editors don't treat templates
as real source files.

Placeholders, replaced verbatim:
    __PROJECT__   project name as given (PascalCase for .NET), e.g. ``MyApi``
    __project__   lower-cased project name, e.g. ``myapi``
"""

from importlib.resources import files
from pathlib import Path, PurePosixPath

PROJECT_TOKEN = "__PROJECT__"
PROJECT_LOWER_TOKEN = "__project__"


def _template_resource(engine: str, relative_path: str):
    parts = [
        "dot_" + part[1:] if part.startswith(".") else part
        for part in PurePosixPath(relative_path).parts
    ]
    parts[-1] += ".tmpl"
    return files("stackforge").joinpath("templates", engine, *parts)


def render_text(engine: str, relative_path: str, project: str) -> str:
    """Returns the template for ``relative_path`` with the project placeholders filled in."""
    content = _template_resource(engine, relative_path).read_text(encoding="utf-8")
    return content.replace(PROJECT_TOKEN, project).replace(PROJECT_LOWER_TOKEN, project.lower())


def render_file(engine: str, base: Path, relative_path: str, project: str) -> None:
    """Writes the rendered template to ``base / relative_path``, creating parent folders."""
    target = base / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_text(engine, relative_path, project))
