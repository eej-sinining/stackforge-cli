"""Renders files from the bundled templates in ``stackforge/templates/<engine>/``.

Template layout mirrors the generated project. Each template file carries a ``.tmpl``
suffix, and a leading ``.`` in a path segment is stored as ``dot_`` (``.env`` ->
``dot_env.tmpl``) so dotfiles survive packaging and editors don't treat templates
as real source files.

Placeholders, replaced verbatim:
    __PROJECT__   project name as given (PascalCase for .NET), e.g. ``MyApi``
    __project__   lower-cased project name, e.g. ``myapi``

Optional features (e.g. ``s3``) wrap their lines in block markers, each on its own line:

    {% if s3 %}
    ...lines kept only when the feature is enabled...
    {% endif %}

Marker lines are always removed; blocks may nest.
"""

import re
from importlib.resources import files
from pathlib import Path, PurePosixPath

PROJECT_TOKEN = "__PROJECT__"
PROJECT_LOWER_TOKEN = "__project__"

_FEATURE_IF = re.compile(r"^\s*\{%\s*if\s+(\w+)\s*%\}\s*$")
_FEATURE_ENDIF = re.compile(r"^\s*\{%\s*endif\s*%\}\s*$")


def _template_resource(engine: str, relative_path: str):
    parts = [
        "dot_" + part[1:] if part.startswith(".") else part
        for part in PurePosixPath(relative_path).parts
    ]
    parts[-1] += ".tmpl"
    return files("stackforge").joinpath("templates", engine, *parts)


def _apply_features(content: str, features: frozenset[str], relative_path: str) -> str:
    kept = []
    enabled_stack: list[bool] = []
    for line in content.splitlines(keepends=True):
        if match := _FEATURE_IF.match(line):
            enabled_stack.append(match.group(1) in features)
        elif _FEATURE_ENDIF.match(line):
            if not enabled_stack:
                raise ValueError(f"{relative_path}: '{{% endif %}}' without a matching '{{% if %}}'")
            enabled_stack.pop()
        elif all(enabled_stack):
            kept.append(line)

    if enabled_stack:
        raise ValueError(f"{relative_path}: '{{% if %}}' block is never closed")
    return "".join(kept)


def render_text(engine: str, relative_path: str, project: str, features: frozenset[str] = frozenset()) -> str:
    """Returns the template for ``relative_path`` with feature blocks resolved and the project placeholders filled in."""
    content = _template_resource(engine, relative_path).read_text(encoding="utf-8")
    content = _apply_features(content, features, relative_path)
    return content.replace(PROJECT_TOKEN, project).replace(PROJECT_LOWER_TOKEN, project.lower())


def render_file(
    engine: str, base: Path, relative_path: str, project: str, features: frozenset[str] = frozenset()
) -> None:
    """Writes the rendered template to ``base / relative_path``, creating parent folders."""
    target = base / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_text(engine, relative_path, project, features))
