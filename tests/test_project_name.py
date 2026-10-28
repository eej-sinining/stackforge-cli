import pytest

from stackforge.project_name import is_valid_project_name, to_pascal_case


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("my_api", "MyApi"),
        ("my-api", "MyApi"),
        ("myApi", "MyApi"),
        ("MyApi", "MyApi"),
        ("aquilaAPI", "AquilaAPI"),
        ("api2go", "Api2Go"),
    ],
)
def test_to_pascal_case(raw, expected):
    assert to_pascal_case(raw) == expected


@pytest.mark.parametrize("name", ["MyApi", "my_api", "my-api", "myApi", "a", "Api2"])
def test_valid_project_names(name):
    assert is_valid_project_name(name)


@pytest.mark.parametrize(
    "name",
    ["", "1api", "_api", "api_", "-api", "my__api", "my--api", "my api", "api!", "../api"],
)
def test_invalid_project_names(name):
    assert not is_valid_project_name(name)
