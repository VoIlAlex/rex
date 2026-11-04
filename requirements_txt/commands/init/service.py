import os.path
import subprocess
import sys

from requirements_txt.utils.check import is_pip_name
from requirements_txt.utils.logging import logger, set_verbose, show_all_done_message
from requirements_txt.utils.override import override_pip
from requirements_txt.utils.path import find_virtualenv


def init_virtual_env(verbose: bool = False):
    set_verbose(verbose)
    logger.info("Installing virtualenv...")
    venv_path = find_virtualenv()
    stdout = sys.stdout if verbose else subprocess.PIPE
    stderr = sys.stderr if verbose else subprocess.PIPE
    if not venv_path:
        subprocess.call(
            [sys.executable, "-m", "pip", "install", "virtualenv"],
            stdout=stdout,
            stderr=stderr,
        )
        subprocess.call(
            [sys.executable, "-m", "virtualenv", "venv"],
            stdout=stdout,
            stderr=stderr,
        )
        shell_command = "ls -l"
        subprocess.run(
            shell_command, shell=True, check=True, text=True, capture_output=True
        )
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
    subprocess.call(
        [f"{venv_path}/bin/pip", "install", "-r", "requirements.txt"],
        stdout=stdout,
        stderr=stderr,
    )
    logger.info(" Done.\n")

    logger.info("Installing to-requirements.txt to virtual environment...")
    if not os.path.exists(f"{venv_path}/bin/requirements-txt"):
        subprocess.call(
            [f"{venv_path}/bin/pip", "install", "to-requirements.txt"],
            stdout=stdout,
            stderr=stderr,
        )
        logger.info(" Done.\n")
    else:
        logger.info(" Skip.\n")

    logger.info("Setting up to-requirements.txt...")
    install_for_venv()
    logger.info(" Done.\n")
    show_all_done_message(venv_path)


def install_for_venv():
    venv_dir = find_virtualenv()

    if venv_dir is None:
        logger.error("Virtualenv not found.")
        return

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
