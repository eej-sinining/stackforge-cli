import json
import urllib.error
import urllib.request
from importlib.metadata import PackageNotFoundError, version

PACKAGE_NAME = "stackforge-cli"
PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"


def get_installed_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.0.0-dev"


def _version_tuple(value: str) -> tuple[int, ...]:
    parts: list[int] = []
    for segment in value.split("."):
        digits = "".join(c for c in segment if c.isdigit())
        if digits:
            parts.append(int(digits))
    return tuple(parts)


def fetch_latest_version(timeout: float = 2.0) -> str | None:
    request = urllib.request.Request(
        PYPI_JSON_URL,
        headers={"Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
        return payload["info"]["version"]
    except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError):
        return None


def notify_if_update_available() -> None:
    from stackforge import ui

    installed = get_installed_version()
    latest = fetch_latest_version()
    if not latest or _version_tuple(latest) <= _version_tuple(installed):
        return

    ui.warn(f"StackForge {latest} is available (you have {installed}).")
    ui.step(f"Update: pip install --upgrade {PACKAGE_NAME}\n")
