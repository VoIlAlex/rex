import os.path
import re
from typing import List, Optional

STATIC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "static",
)
# Present in every pip script patched by REX.
PATCH_MARKER = "requirements_txt"
# `pip`, `pip3`, `pip3.12`, `pip-3.12` -- but not `pip-compile`, `pipx`, etc.
PIP_SCRIPT_REGEX = re.compile(r"^pip(-?\d+(\.\d+)?)?$")


def override_pip(pip_path: str, python_path: str):
    """
    Override the pip script with one presented by to-requirements.txt.

    :param pip_path: path to pip script to override.
    :param python_path: path to python to set as executive for pip script.
    """
    new_pip_path = os.path.join(STATIC_DIR, "new_pip.py")
    with open(pip_path, "w+") as old_pip_file:
        with open(new_pip_path) as new_pip_file:
            old_pip_file.write(new_pip_file.read().format(python_path=python_path))


def is_patched(pip_path: str) -> bool:
    """
    Whether the script is a pip script patched by REX.

    :param pip_path: path to pip script.
    :return: True if the script contains the REX patch.
    """
    try:
        with open(pip_path, "r", errors="ignore") as f:
            return PATCH_MARKER in f.read()
    except OSError:
        return False


def get_shebang_python(pip_path: str) -> Optional[str]:
    """
    Get the python executable from the script's shebang line.

    :param pip_path: path to pip script.
    :return: python path, or None if the script has no shebang.
    """
    with open(pip_path, "r", errors="ignore") as f:
        first_line = f.readline().strip()
    if first_line.startswith("#!") and len(first_line) > 2:
        return first_line[2:].strip()
    return None


def restore_pip(pip_path: str, python_path: Optional[str] = None) -> bool:
    """
    Restore a pip script patched by REX to the script pip itself installs.

    :param pip_path: path to pip script to restore.
    :param python_path: python for the shebang; taken from the patched
        script if not given.
    :return: True if the script was restored, False if it was not patched.
    """
    if not is_patched(pip_path):
        return False
    python_path = python_path or get_shebang_python(pip_path)
    if not python_path:
        raise RuntimeError(f"Cannot determine python executable for {pip_path}.")
    original_pip_path = os.path.join(STATIC_DIR, "original_pip.py")
    with open(original_pip_path) as original_pip_file:
        content = original_pip_file.read().format(python_path=python_path)
    with open(pip_path, "w") as pip_file:
        pip_file.write(content)
    return True


def find_pip_scripts(bin_dir: str) -> List[str]:
    """
    Find pip scripts (`pip`, `pip3`, `pip3.X`, `pip-3.X`) in a directory.

    :param bin_dir: directory to search, e.g. `venv/bin`.
    :return: paths to the scripts.
    """
    if not os.path.isdir(bin_dir):
        return []
    return [
        os.path.join(bin_dir, name)
        for name in sorted(os.listdir(bin_dir))
        if PIP_SCRIPT_REGEX.match(name) and os.path.isfile(os.path.join(bin_dir, name))
    ]


__all__ = [
    "find_pip_scripts",
    "get_shebang_python",
    "is_patched",
    "override_pip",
    "restore_pip",
]
