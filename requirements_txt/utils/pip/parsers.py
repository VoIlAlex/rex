import importlib
import importlib.metadata
import re
from collections import OrderedDict
from typing import Dict, Iterable, List


def canonicalize_name(name: str) -> str:
    """
    Normalize a distribution name as described in PEP 503.

    :param name: distribution name.
    :return: normalized name (lowercase, runs of ``-_.`` replaced by ``-``).
    """
    return re.sub(r"[-_.]+", "-", name).lower()


def get_packages_info(packages_names: List[str]) -> Dict[str, str]:
    """
    Get package name and package version of installed packages by names.

    Uses the standard ``importlib.metadata`` API instead of pip internals,
    which change between pip releases.

    :param packages_names: list of package names to check.
    :return: mapping of package names (as declared in package metadata)
        to package versions, in the order they were requested.
        Packages that are not installed are omitted.
    """
    # Packages may have just been installed or removed in this very process.
    importlib.invalidate_caches()

    requested = [canonicalize_name(name) for name in packages_names]
    found = {}
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata["Name"]
        if not name:
            continue
        key = canonicalize_name(name)
        # The first match wins, following sys.path order (same as imports).
        if key in requested and key not in found:
            found[key] = (name, distribution.version)

    data = {}
    for key in requested:
        if key in found:
            name, version = found[key]
            data[name] = version
    return data


def parse_packages_names(args: Iterable) -> List[str]:
    """
    Parse package names from `pip install` arguments.

    :param args: arguments.
    :return: list of package names.
    """
    packages_names = [
        x.split("==")[0].strip() for x in args if not x.startswith("-") and x != "."
    ]
    return packages_names


def parse_requirements_txt(path: str) -> OrderedDict:
    """
    Parse requirements.txt file.

    :param path: path to requirements.txt.
    :return: mapping of package names to package versions.
    """
    requirements_dict = OrderedDict()
    with open(path, "r") as f:
        requirements = f.readlines()
        for requirement in requirements:
            requirement = requirement.replace("\n", "").strip()
            if requirement.startswith("#") or requirement == "":
                continue
            requirement_split = requirement.split("==")
            if len(requirement_split) == 1:
                requirements_dict[requirement_split[0]] = None
            else:
                requirement_split[1].replace("\n", "")
                requirements_dict[requirement_split[0]] = requirement_split[1]
    return requirements_dict


__all__ = [
    "get_packages_info",
    "parse_packages_names",
    "parse_requirements_txt",
]
