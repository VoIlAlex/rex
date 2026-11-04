import os.path
import subprocess
import sys
from typing import List

import click

from requirements_txt.utils.check import is_pip_name
from requirements_txt.utils.logging import logger, set_verbose, show_all_done_message
from requirements_txt.utils.override import override_pip
from requirements_txt.utils.path import find_virtualenv


class InitError(click.ClickException):
    """A step of `rex init` failed."""


def _run_step(args: List[str], verbose: bool):
    """
    Run a subprocess for an init step and fail loudly if it fails.

    :param args: command to execute.
    :param verbose: whether the output is already streamed to the terminal.
    :raises InitError: if the command exits with a non-zero code.
    """
    if verbose:
        result = subprocess.run(args)
        output = ""
    else:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        output = result.stdout or ""

    if result.returncode != 0:
        logger.info(" Failed.\n")
        message = f"Command `{' '.join(args)}` exited with code {result.returncode}."
        if output.strip():
            message += f"\n\n{output.rstrip()}"
        elif not verbose:
            message += " Re-run with --verbose to see its output."
        raise InitError(message)


def init_virtual_env(verbose: bool = False):
    set_verbose(verbose)
    logger.info("Installing virtualenv...")
    venv_path = find_virtualenv()
    if not venv_path:
        _run_step([sys.executable, "-m", "pip", "install", "virtualenv"], verbose)
        _run_step([sys.executable, "-m", "virtualenv", "venv"], verbose)
        logger.info(" Done.\n")
        venv_path = "./venv"
    else:
        logger.info(" Skip.\n")

    logger.info("Creating requirements.txt...")
    if os.path.exists("./requirements.txt"):
        logger.info(" Skip.\n")
    else:
        with open("./requirements.txt", "w+"):
            ...
        logger.info(" Done.\n")

    logger.info("Installing dependencies...")
    _run_step([f"{venv_path}/bin/pip", "install", "-r", "requirements.txt"], verbose)
    logger.info(" Done.\n")

    logger.info("Installing to-requirements.txt to virtual environment...")
    if not os.path.exists(f"{venv_path}/bin/requirements-txt"):
        _run_step([f"{venv_path}/bin/pip", "install", "to-requirements.txt"], verbose)
        logger.info(" Done.\n")
    else:
        logger.info(" Skip.\n")

    logger.info("Setting up to-requirements.txt...")
    install_for_venv()
    logger.info(" Done.\n")
    show_all_done_message()


def install_for_venv():
    venv_dir = find_virtualenv()

    if venv_dir is None:
        logger.info(" Failed.\n")
        raise InitError("Virtualenv not found.")

    bin_venv_dir = os.path.join(venv_dir, "bin")

    pip_scripts_paths = [
        os.path.join(bin_venv_dir, pip_script_path)
        for pip_script_path in os.listdir(bin_venv_dir)
        if is_pip_name(pip_script_path)
    ]

    for pip_script_path in pip_scripts_paths:
        override_pip(pip_script_path, os.path.join(bin_venv_dir, "python"))


__all__ = [
    "init_virtual_env",
    "install_for_venv",
]
