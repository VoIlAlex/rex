import os
from unittest.mock import patch, Mock

import pytest

from requirements_txt.utils.pip.restrictions import (
    check_git_only_restriction,
    find_git_root,
    find_requirements_txt,
    get_requirements_txt_path,
)


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """
    tmp/
      requirements.txt        <- outside the repository, must be ignored
      repo/.git/
      repo/src/pkg/           <- current directory
    """
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)
    (root / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "requirements.txt").write_text("outside==1.0\n")
    monkeypatch.chdir(root / "src" / "pkg")
    return root


@pytest.fixture()
def no_repo(tmp_path, monkeypatch):
    work = tmp_path / "work" / "sub"
    work.mkdir(parents=True)
    monkeypatch.chdir(work)
    return work


class TestFindGitRoot:
    def test_from_subdirectory(self, repo):
        assert find_git_root() == str(repo)

    def test_git_file_worktree(self, tmp_path, monkeypatch):
        (tmp_path / ".git").write_text("gitdir: /elsewhere\n")
        (tmp_path / "a").mkdir()
        monkeypatch.chdir(tmp_path / "a")
        assert find_git_root() == str(tmp_path)


class TestFindRequirementsTxt:
    def test_found_at_repository_root(self, repo):
        (repo / "requirements.txt").write_text("")
        assert find_requirements_txt() == str(repo / "requirements.txt")

    def test_closest_one_wins(self, repo):
        (repo / "requirements.txt").write_text("")
        (repo / "src" / "requirements.txt").write_text("")
        assert find_requirements_txt() == str(repo / "src" / "requirements.txt")

    def test_search_stops_at_repository_root(self, repo):
        assert find_requirements_txt() is None

    def test_outside_repository_only_current_directory(self, no_repo):
        (no_repo.parent / "requirements.txt").write_text("")
        assert find_requirements_txt() is None
        (no_repo / "requirements.txt").write_text("")
        assert find_requirements_txt() == str(no_repo / "requirements.txt")

    def test_directory_named_requirements_txt_is_ignored(self, repo):
        (repo / "src" / "pkg" / "requirements.txt").mkdir()
        (repo / "requirements.txt").write_text("")
        assert find_requirements_txt() == str(repo / "requirements.txt")


@patch("requirements_txt.utils.pip.restrictions.get_config_value")
class TestCheckGitOnlyRestriction:
    def test_not_enabled(self, get_config_value_mock: Mock, no_repo):
        get_config_value_mock.return_value = False
        assert check_git_only_restriction() is True
        get_config_value_mock.assert_called_once_with("only_git")

    def test_enabled_in_repository_subdirectory(self, get_config_value_mock, repo):
        get_config_value_mock.return_value = True
        assert check_git_only_restriction() is True

    def test_enabled_outside_repository(self, get_config_value_mock, no_repo):
        get_config_value_mock.return_value = True
        assert check_git_only_restriction() is False


@patch("requirements_txt.utils.pip.restrictions.get_config_value")
class TestGetRequirementsTxtPath:
    def test_not_found(self, get_config_value: Mock, no_repo):
        assert get_requirements_txt_path(try_create=False) == (None, False)
        get_config_value.assert_not_called()

    def test_found_in_current_directory(self, _: Mock, no_repo):
        (no_repo / "requirements.txt").write_text("")
        expected = str(no_repo / "requirements.txt")
        assert get_requirements_txt_path(try_create=False) == (expected, False)

    def test_found_in_parent_directory(self, _: Mock, repo):
        (repo / "requirements.txt").write_text("")
        expected = str(repo / "requirements.txt")
        assert get_requirements_txt_path(try_create=True) == (expected, False)

    def test_create_not_allowed(self, get_config_value: Mock, no_repo):
        get_config_value.return_value = False
        assert get_requirements_txt_path(try_create=True) == (None, False)
        assert not os.path.exists(no_repo / "requirements.txt")

    def test_created_in_current_directory_outside_repository(
        self, get_config_value: Mock, no_repo
    ):
        get_config_value.return_value = True
        expected = str(no_repo / "requirements.txt")
        assert get_requirements_txt_path(try_create=True) == (expected, True)
        assert os.path.isfile(expected)
        get_config_value.assert_called_once_with("allow_create")

    def test_created_at_repository_root(self, get_config_value: Mock, repo):
        get_config_value.return_value = True
        expected = str(repo / "requirements.txt")
        assert get_requirements_txt_path(try_create=True) == (expected, True)
        assert os.path.isfile(expected)
