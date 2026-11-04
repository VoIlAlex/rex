"""
Keep the REX patch in place when pip upgrades itself.

Upgrading pip reinstalls its console scripts (`pip`, `pip3`, `pip3.X`),
which silently replaces the patched scripts installed by REX.
"""
import os
import re
from typing import Iterable, List

from requirements_txt.utils.override import override_pip

# `pip`, `pip3`, `pip3.12`, `pip-3.12` -- but not `pip-compile`, `pipx`, etc.
PIP_SCRIPT_REGEX = re.compile(r"^pip(-?\d+(\.\d+)?)?$")
# A `pip` requirement: `pip`, `pip==24.0`, `PIP>=23`, `pip[extra]`;
# but not `pip-tools` or `pipx`.
PIP_REQUIREMENT_REGEX = re.compile(r"^pip(?![\w.-])", re.IGNORECASE)
PATCH_MARKER = "requirements_txt"


def is_pip_self_install(args: Iterable[str]) -> bool:
    """
    Whether `pip install <args>` (re)installs pip itself.

    :param args: arguments of `pip install`.
    :return: True if pip is among the requested packages.
    """
    return any(
        not arg.startswith("-") and PIP_REQUIREMENT_REGEX.match(arg.strip())
        for arg in args
    )


def is_patched(script_path: str) -> bool:
    """
    Whether the script at the given path is a REX-patched pip script.

    :param script_path: path to pip script.
    :return: True if the script contains the REX patch.
    """
    try:
        with open(script_path, "r", errors="ignore") as f:
            return PATCH_MARKER in f.read()
    except OSError:
        return False


def repatch_pip_scripts(bin_dir: str, python_path: str) -> List[str]:
    """
    Re-apply the REX patch to pip scripts that lost it.

    :param bin_dir: directory with the pip scripts (e.g. `venv/bin`).
    :param python_path: python executable to set in the scripts' shebang.
    :return: names of the scripts that were patched again.
    """
    repatched = []
    for name in sorted(os.listdir(bin_dir)):
        script_path = os.path.join(bin_dir, name)
        if not PIP_SCRIPT_REGEX.match(name) or not os.path.isfile(script_path):
            continue
        if is_patched(script_path):
            continue
        override_pip(script_path, python_path)
        repatched.append(name)
    return repatched


__all__ = [
    "is_pip_self_install",
    "is_patched",
    "repatch_pip_scripts",
]
