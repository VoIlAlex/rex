import logging
import os.path
from collections import OrderedDict
from typing import Iterable, List
from requirements_txt.utils.pip.parsers import (
    parse_packages_names,
    get_packages_info,
    parse_requirements_txt,
)
from requirements_txt.utils.pip.restrictions import (
    check_git_only_restriction,
    get_requirements_txt_path,
)


def is_package_folder(path: str) -> bool:
    if os.path.exists(path):
        if os.path.exists(os.path.join(path, "setup.py")):
            return True
    return False


def cluster_package_names(package_names: List[str]):
    pypi_packages = []
    git_packages = []
    file_system_packages = []

    for package_name in package_names:
        if package_name.startswith("git+"):
            git_packages.append(package_name)
        elif package_name.startswith(".") or is_package_folder(package_name):
            file_system_packages.append(package_name)
        else:
            pypi_packages.append(package_name)

    return dict(
        pypi_packages=pypi_packages,
        git_packages=git_packages,
        file_system_packages=file_system_packages,
    )


def add_installed_packages_to_requirements_txt(args: Iterable):
    """
    Add installed packages to requirements.txt or update their versions.

    :param args: arguments of `pip install`.
    """
    args_packages_names = parse_packages_names(args)
    clustered_packages_names = cluster_package_names(args_packages_names)
    packages = get_packages_info(clustered_packages_names["pypi_packages"])

    if not check_git_only_restriction():
        logging.warning("Cannot write to requirements.txt. git_only flag is set.")
        return

    requirements_txt_path, created = get_requirements_txt_path(try_create=True)

    if requirements_txt_path is None and not created:
        logging.warning(
            "requirements.txt not found. Specify allow_create "
            "config key if you want it to create automatically."
        )
        return

    requirements_dict = OrderedDict()

    if not created:
        requirements_dict = parse_requirements_txt(requirements_txt_path)

    packages_without_version = []
    for package_name, package_version in packages.items():
        if not package_version:
            if package_name not in requirements_dict:
                packages_without_version.append(package_name)
        else:
            requirements_dict[package_name] = package_version
    for package_name in clustered_packages_names["git_packages"]:
        requirements_dict[package_name] = None
    for package_name in clustered_packages_names["file_system_packages"]:
        requirements_dict[package_name] = None

    clustered_packages_names = cluster_package_names(list(requirements_dict.keys()))
    with open(requirements_txt_path, "w+") as f:
        lines_to_write = []
        lines_to_write += [
            f"{package_name}\n" for package_name in packages_without_version
        ]
        lines_to_write += [
            f"{package_name}=={requirements_dict[package_name]}\n"
            for package_name in clustered_packages_names["pypi_packages"]
        ]
        lines_to_write += [
            f"{package_name}\n"
            for package_name in clustered_packages_names["git_packages"]
        ]
        lines_to_write += [
            f"{package_name}\n"
            for package_name in clustered_packages_names["file_system_packages"]
        ]
        f.writelines(lines_to_write)


def remove_uninstalled_packages_from_requirements_txt(args: Iterable):
    """
    Remove uninstalled package from requirements.txt.

    :param args: arguments of `pip install`.
    """
    args_packages_names = parse_packages_names(args)
    packages = get_packages_info(args_packages_names)

    if not check_git_only_restriction():
        logging.warning("Cannot write to requirements.txt. git_only flag is set.")
        return

    requirements_txt_path, _ = get_requirements_txt_path(try_create=False)

    if requirements_txt_path is None:
        logging.warning("requirements.txt not found")
        return

    requirements_dict = parse_requirements_txt(requirements_txt_path)
    for package_name in list(requirements_dict.keys()):
        if package_name in args_packages_names and package_name not in packages:
            del requirements_dict[package_name]

    clustered_packages_names = cluster_package_names(list(requirements_dict.keys()))

    with open(requirements_txt_path, "w+") as f:
        lines_to_write = []
        lines_to_write += [
            f"{package_name}=={requirements_dict[package_name]}\n"
            for package_name in clustered_packages_names["pypi_packages"]
        ]
        lines_to_write += [
            f"{package_name}\n"
            for package_name in clustered_packages_names["git_packages"]
        ]
        lines_to_write += [
            f"{package_name}\n"
            for package_name in clustered_packages_names["file_system_packages"]
        ]
        f.writelines(lines_to_write)


__all__ = [
    "add_installed_packages_to_requirements_txt",
    "remove_uninstalled_packages_from_requirements_txt",
]
