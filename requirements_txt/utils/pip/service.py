import logging
import os.path
from collections import OrderedDict
from typing import Iterable, List
from requirements_txt.utils.files import (
    DEFAULT_ENCODING,
    read_text_file,
    write_text_file,
)
from requirements_txt.utils.pip.parsers import (
    canonicalize_name,
    get_requirement_key,
    is_direct_reference,
    parse_packages_names,
    split_requirement,
    get_packages_info,
    parse_requirements_txt,
)
from requirements_txt.utils.pip.restrictions import (
    check_git_only_restriction,
    get_requirements_txt_path,
)


def _format_requirement(key: str, version) -> str:
    # Lines without a pinned version (`flask`, `foo>=1.0`) are kept verbatim.
    return f"{key}=={version}\n" if version else f"{key}\n"


def _write_requirements_txt(path: str, lines: List[str]):
    """
    Write requirements.txt, keeping the encoding and line endings it had.
    """
    encoding, newline = DEFAULT_ENCODING, "\n"
    if os.path.exists(path) and os.path.getsize(path) > 0:
        _, encoding, newline = read_text_file(path)
    write_text_file(path, "".join(lines), encoding=encoding, newline=newline)


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
        elif package_name.startswith((".", "/")) or is_package_folder(package_name):
            file_system_packages.append(package_name)
        elif is_direct_reference(package_name):
            # `name @ url`, archive URLs: written as is, like git packages.
            git_packages.append(package_name)
        else:
            pypi_packages.append(package_name)

    return dict(
        pypi_packages=pypi_packages,
        git_packages=git_packages,
        file_system_packages=file_system_packages,
    )


def _set_requirement(requirements_dict: OrderedDict, key: str, version):
    """
    Set a requirement, replacing an existing line for the same project in place.

    `requests`, `Requests>=2` and `requests[socks]==1.0` all refer to the
    same project, so installing one of them must not add a duplicate line.
    """
    project = get_requirement_key(key)
    for existing_key in list(requirements_dict.keys()):
        if project is not None and get_requirement_key(existing_key) == project:
            items = [
                (key, version) if k == existing_key else (k, v)
                for k, v in requirements_dict.items()
                if k == existing_key or get_requirement_key(k) != project
            ]
            requirements_dict.clear()
            requirements_dict.update(items)
            return
    requirements_dict[key] = version


def add_installed_packages_to_requirements_txt(args: Iterable):
    """
    Add installed packages to requirements.txt or update their versions.

    :param args: arguments of `pip install`.
    """
    args_packages_names = parse_packages_names(args)
    clustered_packages_names = cluster_package_names(args_packages_names)
    # `requests[socks]` is looked up as `requests`; extras are written back.
    extras = {}
    pypi_names = []
    for spec in clustered_packages_names["pypi_packages"]:
        name, spec_extras = split_requirement(spec) or (spec, "")
        extras[canonicalize_name(name)] = spec_extras
        pypi_names.append(name)
    packages = get_packages_info(pypi_names)

    if not check_git_only_restriction():
        logging.warning("Cannot write to requirements.txt. git_only flag is set.")
        return

    requirements_txt_path, created = get_requirements_txt_path()

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
        key = package_name + extras.get(canonicalize_name(package_name), "")
        if not package_version:
            if package_name not in requirements_dict:
                packages_without_version.append(key)
        else:
            _set_requirement(requirements_dict, key, package_version)
    for package_name in clustered_packages_names["git_packages"]:
        requirements_dict[package_name] = None
    for package_name in clustered_packages_names["file_system_packages"]:
        requirements_dict[package_name] = None

    clustered_packages_names = cluster_package_names(list(requirements_dict.keys()))
    lines_to_write = []
    lines_to_write += [f"{package_name}\n" for package_name in packages_without_version]
    lines_to_write += [
        _format_requirement(package_name, requirements_dict[package_name])
        for package_name in clustered_packages_names["pypi_packages"]
    ]
    lines_to_write += [
        f"{package_name}\n" for package_name in clustered_packages_names["git_packages"]
    ]
    lines_to_write += [
        f"{package_name}\n"
        for package_name in clustered_packages_names["file_system_packages"]
    ]
    _write_requirements_txt(requirements_txt_path, lines_to_write)


def remove_uninstalled_packages_from_requirements_txt(args: Iterable):
    """
    Remove uninstalled package from requirements.txt.

    :param args: arguments of `pip install`.
    """
    args_packages_names = parse_packages_names(args, command="uninstall")
    packages = get_packages_info(args_packages_names)

    if not check_git_only_restriction():
        logging.warning("Cannot write to requirements.txt. git_only flag is set.")
        return

    requirements_txt_path, _ = get_requirements_txt_path(try_create=False)

    if requirements_txt_path is None:
        logging.warning("requirements.txt not found")
        return

    uninstalled = {canonicalize_name(name) for name in args_packages_names} - {
        canonicalize_name(name) for name in packages
    }
    requirements_dict = parse_requirements_txt(requirements_txt_path)
    for package_name in list(requirements_dict.keys()):
        if get_requirement_key(package_name) in uninstalled:
            del requirements_dict[package_name]

    clustered_packages_names = cluster_package_names(list(requirements_dict.keys()))

    lines_to_write = []
    lines_to_write += [
        _format_requirement(package_name, requirements_dict[package_name])
        for package_name in clustered_packages_names["pypi_packages"]
    ]
    lines_to_write += [
        f"{package_name}\n" for package_name in clustered_packages_names["git_packages"]
    ]
    lines_to_write += [
        f"{package_name}\n"
        for package_name in clustered_packages_names["file_system_packages"]
    ]
    _write_requirements_txt(requirements_txt_path, lines_to_write)


__all__ = [
    "add_installed_packages_to_requirements_txt",
    "remove_uninstalled_packages_from_requirements_txt",
]
