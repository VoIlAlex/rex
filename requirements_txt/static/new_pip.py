#!{python_path}
# -*- coding: utf-8 -*-
import os
import re
import sys

from pip._internal.cli.main import main
from pip._internal.cli.main_parser import parse_command

requirements_handler = False
PIP_RT_VERSION = 2

try:
    from requirements_txt.utils.pip import (
        add_installed_packages_to_requirements_txt,
        remove_uninstalled_packages_from_requirements_txt,
    )
    from requirements_txt.utils.config import get_config_value
    from requirements_txt.utils.pip.selfupdate import (
        is_pip_self_install,
        repatch_pip_scripts,
    )

    try:
        from requirements_txt import __version__
    except ImportError:
        __version__ = "1.0.0"

    major_version = int(__version__.split(".")[0])
    if major_version != PIP_RT_VERSION:
        sys.stdout.write(
            "Module to-requirements.txt major version does not match pip.py. "
        )
        sys.stdout.write(
            "(to-requirements.txt==%s, pip.py==%s) \n"
            % (str(major_version), str(PIP_RT_VERSION))
        )
        sys.stdout.write("To fix this issue and continue to use to-requirements.txt:\n")
        sys.stdout.write(
            "Option 1: pip install to-requirements.txt==$s.*\n" % PIP_RT_VERSION
        )
        sys.stdout.write("Option 2: requirements-txt install")
    else:
        requirements_handler = True
except Exception:
    ...

if __name__ == "__main__":
    command, args = parse_command(sys.argv[1:])
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    res = main()
    if requirements_handler and res == 0:
        if command == "install" and is_pip_self_install(args):
            # Upgrading pip replaces its scripts, including this one.
            bin_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            repatched = repatch_pip_scripts(bin_dir, sys.executable)
            if repatched:
                sys.stdout.write(
                    "rex: pip was reinstalled; restored requirements.txt "
                    "synchronization for: %s\n" % ", ".join(repatched)
                )
        disable = get_config_value("disable")
        if not disable:
            if command == "install" and "-r" not in args:
                add_installed_packages_to_requirements_txt(args)
            if command == "uninstall":
                remove_uninstalled_packages_from_requirements_txt(args)
    sys.exit(res)
