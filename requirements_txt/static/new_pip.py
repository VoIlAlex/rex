#!{python_path}
# -*- coding: utf-8 -*-
import os
import re
import sys

from pip._internal.cli.main import main
from pip._internal.cli.main_parser import parse_command

requirements_handler = False
PIP_RT_VERSION = 2


def _report_error(message):
    sys.stderr.write("WARNING: rex: %s\n" % message)
    if os.environ.get("REX_DEBUG"):
        import traceback

        traceback.print_exc()
    else:
        sys.stderr.write("WARNING: rex: set REX_DEBUG=1 to see the full traceback.\n")


try:
    from requirements_txt.utils.pip import (
        add_installed_packages_to_requirements_txt,
        remove_uninstalled_packages_from_requirements_txt,
    )
    from requirements_txt.utils.config import get_config_value

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
            "Option 1: pip install to-requirements.txt==%s.*\n" % PIP_RT_VERSION
        )
        sys.stdout.write("Option 2: requirements-txt install\n")
    else:
        requirements_handler = True
except ImportError as e:
    if (e.name or "").split(".")[0] != "requirements_txt":
        _report_error("requirements.txt will not be updated: %r" % e)
    # Otherwise REX was uninstalled from this environment: behave like plain pip.
except Exception as e:
    _report_error("requirements.txt will not be updated: %r" % e)

if __name__ == "__main__":
    command, args = parse_command(sys.argv[1:])
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    res = main()
    if requirements_handler and res == 0:
        # pip itself succeeded: a failure here must never change its exit code.
        try:
            disable = get_config_value("disable")
            if not disable:
                if command == "install" and "-r" not in args:
                    add_installed_packages_to_requirements_txt(args)
                if command == "uninstall":
                    remove_uninstalled_packages_from_requirements_txt(args)
        except Exception as e:
            _report_error("failed to update requirements.txt: %r" % e)
    sys.exit(res)
