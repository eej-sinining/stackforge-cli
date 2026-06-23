import re

_CAMEL_PARTS = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)|\d+")


def is_valid_project_name(name: str) -> bool:
    if not name or not name[0].isalpha():
        return False
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        return False
    if name.startswith(("-", "_")) or name.endswith(("-", "_")):
        return False
    if "__" in name or "--" in name:
        return False
    return True


def _title_part(part: str) -> str:
    if not part:
        return ""
    if part.isdigit():
        return part
    return part[0].upper() + part[1:]


def to_pascal_case(name: str) -> str:
    if "_" in name:
        parts = name.split("_")
    elif "-" in name:
        parts = name.split("-")
    else:
        parts = _CAMEL_PARTS.findall(name) or [name]

    return "".join(_title_part(part) for part in parts if part)
