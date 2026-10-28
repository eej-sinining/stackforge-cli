import shutil
import subprocess
from pathlib import Path

import pytest

import stackforge.engines.dotnet.scaffolder as scaffolder
from stackforge.engines.dotnet import features

PROJECT = "SampleApi"


def _scaffold(base: Path, monkeypatch, with_git: bool, enabled: frozenset[str] = frozenset()) -> Path:
    if not with_git:
        monkeypatch.setattr(scaffolder, "git_init", lambda base, project: None)
    base.mkdir(parents=True)
    scaffolder.scaffold_folders(base, PROJECT, enabled)
    return base


@pytest.fixture
def scaffolded(tmp_path, monkeypatch) -> Path:
    """A freshly scaffolded .NET project, without the git repository."""
    return _scaffold(tmp_path / PROJECT, monkeypatch, with_git=False)


@pytest.fixture
def scaffolded_s3(tmp_path, monkeypatch) -> Path:
    """A freshly scaffolded S3-ready .NET project, without the git repository."""
    return _scaffold(tmp_path / "s3" / PROJECT, monkeypatch, with_git=False, enabled=frozenset({features.S3}))


@pytest.fixture
def scaffolded_with_git(tmp_path, monkeypatch) -> Path:
    """A freshly scaffolded .NET project including `git init`, initial commit and branches."""
    if shutil.which("git") is None:
        pytest.skip("git is not installed")

    # CI runners have no git identity; the initial commit needs one.
    for key, value in {
        "GIT_AUTHOR_NAME": "StackForge Tests",
        "GIT_AUTHOR_EMAIL": "tests@stackforge.invalid",
        "GIT_COMMITTER_NAME": "StackForge Tests",
        "GIT_COMMITTER_EMAIL": "tests@stackforge.invalid",
    }.items():
        monkeypatch.setenv(key, value)

    return _scaffold(tmp_path / PROJECT, monkeypatch, with_git=True)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout
