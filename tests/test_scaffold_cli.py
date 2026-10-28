from dataclasses import replace

import pytest

from stackforge import scaffold
from stackforge.engines.dotnet import features


def _answers(monkeypatch, *answers):
    """Feeds ``answers`` to ``ui.prompt``; fails the test if the CLI asks for more."""
    remaining = list(answers)

    def fake_prompt(label):
        assert remaining, f"unexpected prompt: {label}"
        return remaining.pop(0)

    monkeypatch.setattr(scaffold.ui, "prompt", fake_prompt)
    return remaining


def test_menu_lists_only_dotnet_and_exit():
    assert scaffold.MENU_CHOICES == ("dotnet", "exit")


@pytest.mark.parametrize("choice", ["", "django", "fastapi", "flask", "next"])
def test_menu_rejects_empty_and_unknown_choices(monkeypatch, capsys, choice):
    _answers(monkeypatch, choice)

    assert scaffold.select_framework() == ""
    assert "Options: dotnet, exit" in capsys.readouterr().out


@pytest.mark.parametrize("choice, expected", [("dotnet", "dotnet"), ("DOTNET", "dotnet"), ("exit", "exit")])
def test_menu_accepts_explicit_choices(monkeypatch, choice, expected):
    _answers(monkeypatch, choice)

    assert scaffold.select_framework() == expected


@pytest.mark.parametrize("answers, expected", [
    (["y"], frozenset({features.S3})),
    (["yes"], frozenset({features.S3})),
    (["n"], frozenset()),
    (["", "maybe", "no"], frozenset()),
])
def test_dotnet_s3_question_requires_explicit_answer(monkeypatch, answers, expected):
    remaining = _answers(monkeypatch, *answers)

    assert scaffold.prompt_dotnet_features() == expected
    assert remaining == []


@pytest.mark.parametrize("s3_answer, expected", [("y", frozenset({features.S3})), ("n", frozenset())])
def test_main_scaffolds_selected_framework_with_features(monkeypatch, tmp_path, s3_answer, expected):
    calls = []
    monkeypatch.setattr(scaffold, "notify_if_update_available", lambda: None)
    monkeypatch.setattr(scaffold.Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.setitem(
        scaffold.FRAMEWORKS,
        "dotnet",
        replace(
            scaffold.FRAMEWORKS["dotnet"],
            scaffold=lambda base, project, enabled: calls.append((base, project, enabled)),
        ),
    )
    # Empty choice is rejected first, then .NET, S3 answer, project name, and exit.
    remaining = _answers(monkeypatch, "", "dotnet", s3_answer, "my-api", "exit")

    scaffold.main()

    assert calls == [(tmp_path / "stackforge" / "MyApi", "MyApi", expected)]
    assert remaining == []
