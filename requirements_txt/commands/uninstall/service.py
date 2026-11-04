import os
from typing import List

from requirements_txt.utils.logging import logger
from requirements_txt.utils.override import (
    PIP_SCRIPT_REGEX,
    find_pip_scripts,
    is_patched,
    restore_pip,
)
from requirements_txt.utils.path import get_pip_path


def _get_bin_dirs() -> List[str]:
    """
    Directories of the `pip` and `pip3` found on PATH: the ones `rex install`
    patches, and the virtual environment `rex init` patches once activated.
    """
    bin_dirs = []
    for pip in ["pip", "pip3"]:
        pip_path, _ = get_pip_path(pip)
        if pip_path:
            bin_dir = os.path.dirname(os.path.abspath(pip_path))
            if bin_dir not in bin_dirs:
                bin_dirs.append(bin_dir)
    return bin_dirs


def uninstall() -> List[str]:
    """
    Restore pip scripts patched by REX to their original state.

    :return: restored script paths.
    """
    restored = []
    for bin_dir in _get_bin_dirs():
        for pip_script_path in find_pip_scripts(bin_dir):
            if restore_pip(pip_script_path):
                logger.info(f'Restored "{pip_script_path}"\n')
                restored.append(pip_script_path)

        # `rex init` patches every script whose name starts with "pip",
        # including e.g. `pip-compile`. Their original content is unknown,
        # so they cannot be restored here.
        for name in sorted(os.listdir(bin_dir)):
            path = os.path.join(bin_dir, name)
            if not name.startswith("pip") or PIP_SCRIPT_REGEX.match(name):
                continue
            if os.path.isfile(path) and is_patched(path):
                logger.warning(
                    f'"{path}" was overwritten by to-requirements.txt and cannot '
                    "be restored automatically. Reinstall the package that "
                    "provides it.\n"
                )
    return restored


__all__ = [
    "uninstall",
]
