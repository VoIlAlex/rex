import os
from typing import Optional, Tuple


from requirements_txt.utils.config import get_config_value

REQUIREMENTS_TXT = "requirements.txt"


def find_git_root(path: Optional[str] = None) -> Optional[str]:
    """
    Find the root of the git repository containing the path.

    :param path: directory to start from (current directory by default).
    :return: repository root, or None if path is not inside a git repository.
    """
    path = os.path.abspath(path or os.getcwd())
    while True:
        # `.git` is a file in worktrees and submodules.
        if os.path.exists(os.path.join(path, ".git")):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent


def find_requirements_txt(path: Optional[str] = None) -> Optional[str]:
    """
    Find the requirements.txt the current directory belongs to.

    Inside a git repository, the current directory and its parents up to the
    repository root are searched, so commands work from any subdirectory.
    Outside a repository only the current directory is searched, to avoid
    picking up an unrelated requirements.txt from e.g. the home directory.

    :param path: directory to start from (current directory by default).
    :return: path to requirements.txt, or None if not found.
    """
    path = os.path.abspath(path or os.getcwd())
    git_root = find_git_root(path)
    while True:
        candidate = os.path.join(path, REQUIREMENTS_TXT)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(path)
        if git_root is None or path == git_root or parent == path:
            return None
        path = parent


def check_git_only_restriction() -> bool:
    """
    Check whether git_only configuration condition is met.

    :return: True if everything is okay.
    """
    git_only = get_config_value("only_git")
    if git_only:
        return find_git_root() is not None
    return True


def get_requirements_txt_path(try_create: bool = False) -> Tuple[Optional[str], bool]:
    """
    Get requirements.txt path. Create one if not exists, try_create is specified
    configuration doesn't restrict it.

    The file is searched for with `find_requirements_txt`. A new file is
    created at the git repository root, or in the current directory outside
    a repository.

    :param try_create: whether to try to create requirements.txt if not exists.
    :return: path to requirements_txt, and whether it's newly created.
    """
    requirements_txt_path = find_requirements_txt()
    if requirements_txt_path is not None:
        return requirements_txt_path, False

    if try_create and get_config_value("allow_create"):
        requirements_txt_path = os.path.join(
            find_git_root() or os.getcwd(), REQUIREMENTS_TXT
        )
        with open(requirements_txt_path, "w+"):
            ...
        return requirements_txt_path, True

    return None, False


__all__ = [
    "check_git_only_restriction",
    "find_git_root",
    "find_requirements_txt",
    "get_requirements_txt_path",
]
