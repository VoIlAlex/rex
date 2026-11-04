import logging
import os
import sys
from typing import Optional

from colored import attr, fg

from requirements_txt.utils.consts import ALL_DONE_TITLE

logger = logging.getLogger("requirements-txt")
logger.setLevel(logging.INFO)
logger_handler = logging.StreamHandler(sys.stdout)
logger_formatter = logging.Formatter(
    f'{fg(15)}|===| %(message)s{attr(1)}{attr("reset")}'
)
logger_handler.setFormatter(logger_formatter)
logger_handler.terminator = ""
logger.addHandler(logger_handler)


def set_verbose(verbose: bool = False):
    """
    Set verbosity of logger.
    :param verbose: whether logger is verbose.
    """
    if verbose:
        logger_handler.terminator = "\n"
    else:
        logger_handler.terminator = ""


def _use_colors() -> bool:
    # https://no-color.org; also no escape codes when output is piped.
    return not os.environ.get("NO_COLOR") and sys.stdout.isatty()


def _style(text: str, *styles: str) -> str:
    if not _use_colors():
        return text
    return "".join(styles) + text + attr("reset")


def show_all_done_message(venv_path: Optional[str] = None):
    """
    Print the summary shown at the end of `rex init`.

    :param venv_path: path to the virtual environment that was set up.
    """
    venv_path = os.path.relpath(venv_path) if venv_path else "venv"
    activate_path = os.path.join(venv_path, "bin", "activate")
    # Set by the `rex` shell script when it runs in sourced mode (`. rex i`),
    # in which case it activates the environment itself.
    sourced = os.environ.get("REX_SOURCED") == "1"

    lines = [
        "",
        _style(f"✔ {ALL_DONE_TITLE}", fg("green"), attr("bold")),
        "",
        f"  Virtual environment  {venv_path}",
        "  Requirements file    requirements.txt",
        "",
        _style("  Next steps", attr("bold")),
    ]
    if sourced:
        lines.append("    The virtual environment is activated.")
    else:
        lines.append(f"    {_style('source ' + activate_path, fg('cyan'))}")
    lines += [
        f"    {_style('pip install <package>', fg('cyan'))}"
        "    requirements.txt is updated automatically",
        "",
    ]
    print("\n".join(lines))


__all__ = [
    "logger",
    "set_verbose",
    "show_all_done_message",
]
