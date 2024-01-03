"""Unit tests for generating the badges for the README file."""

from unittest.mock import MagicMock, patch

import pytest

from readmeai.markdown.badges import (
    _read_badge_file,
    build_html_badges,
    format_html_badges,
    shields_icons,
    skill_icons,
)


@pytest.mark.parametrize(
    "badges, expected",
    [
        ([], ""),
        (
            [
                "https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white"
            ],
            '<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">',
        ),
    ],
)
def test_format_html_badges(badges, expected):
    """Tests the format_html method."""
    assert format_html_badges(badges) == expected


@pytest.mark.parametrize(
    "dependencies, svg_icons, style, expected",
    [
        ([], {}, "skills", ""),
        (
            ["python"],
            {
                "python": [
                    "https://img.shields.io/badge/Python-3776AB.svg?style={0}&logo=Python&logoColor=white",
                    "3776AB",
                ],
            },
            "flat",
            '<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">',
        ),
    ],
)
def test_build_html_badges(dependencies, svg_icons, style, expected):
    """Tests the generate_html method."""
    assert (
        build_html_badges(
            dependencies,
            svg_icons,
            style,
        )
        == expected
    )


def test_shields_icons_success(config):
    """Tests shields_icons with valid inputs."""
    mock_config = config
    mock_config.git.source = "github.com"
    mock_config.files.shields_icons = config.files.shields_icons
    mock_config.md.badges_style = "flat"

    mock_helper = MagicMock()
    mock_helper.language_setup = {"Python": ["install", "run", "test"]}

    deps = ["Python", "JavaScript"]

    with patch("readmeai.markdown.badges._read_badge_file") as mock_read:
        mock_read.return_value = {
            "python": [
                "https://img.shields.io/badge/Python-3776AB.svg?style={0}&logo=Python&logoColor=white",
                "3776AB",
            ],
        }
        result = shields_icons(mock_config, deps, "full_name")
        assert "Python" in result
        assert "3776AB" in result
        assert "flat" in result


def test_skill_icons_success(config):
    """Tests skill_icons with valid inputs."""
    mock_config = config
    mock_config.files.skill_icons = config.files.skill_icons
    mock_config.md.badges_style = "skills-light"
    mock_icons = {
        "icons": {"names": ["fastapi", "py", "redis", "md", "github", "git"]},
        "url": {"base_url": "https://skillicons.dev/icons?i="},
    }
    deps = ["fastapi", "py", "redis", "md", "github", "git"]

    with patch("readmeai.markdown.badges._read_badge_file") as mock_read:
        mock_read.return_value = mock_icons
        result = skill_icons(mock_config, deps)
        assert result.startswith("<a href=") is True
        assert result.endswith("\n</a>\n") is True
        assert "&theme=light" in result
        assert """<a href="https://skillicons.dev">""" in result
        assert (
            """<img src="https://skillicons.dev/icons?i=fastapi,py,redis,md,github,git&theme=light">\n</a>\n"""
            in result
        )


def test_read_badge_file_success(config, monkeypatch):
    """Tests the _read_badge_file method for successful file read."""
    badge_file_path = config.files.shields_icons
    mock_file_handler = MagicMock()
    mock_file_handler.read.return_value = {
        "icons": {"names": ["Python", "JavaScript"]},
        "url": {"base_url": "http://example.com/"},
    }
    monkeypatch.setattr("readmeai.core.factory.FileHandler", mock_file_handler)
    assert isinstance(_read_badge_file(badge_file_path), dict)


def test_read_badge_file_exception(config, monkeypatch):
    """Tests the _read_badge_file method for exception handling."""
    badge_file_path = "invalid_path"
    mock_file_handler = MagicMock()
    mock_file_handler.read.side_effect = Exception("File read error")
    monkeypatch.setattr("readmeai.core.factory.FileHandler", mock_file_handler)

    with pytest.raises(Exception) as exc_info:
        _read_badge_file(badge_file_path)
    assert isinstance(exc_info.value, Exception)
