import importlib
import importlib.metadata
import re
from collections import OrderedDict
from typing import Dict, Iterable, List, Optional, Tuple

from requirements_txt.utils.files import read_text_file


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


# A requirement that starts with a project name, optionally with extras:
# `requests`, `requests[socks]>=2.0`, `zope.interface==5.0; python_version>"3"`.
REQUIREMENT_NAME_REGEX = re.compile(
    r"^\s*([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)\s*(\[[^\]]*\])?"
)


def is_direct_reference(spec: str) -> bool:
    """
    Whether a requirement points to a location rather than to a PyPI project:
    a VCS URL, an archive URL, a local path or a PEP 508 `name @ url`.

    :param spec: requirement as passed to pip.
    :return: True if spec is a direct reference.
    """
    spec = spec.strip()
    return spec.startswith((".", "/", "git+")) or "://" in spec or "@" in spec


def split_requirement(spec: str) -> Optional[Tuple[str, str]]:
    """
    Split a requirement into a project name and its extras.

    :param spec: requirement, e.g. `requests[socks]>=2.0`.
    :return: (name, extras) e.g. ("requests", "[socks]"), with extras
        normalized; None if spec is a direct reference or not a requirement.
    """
    if is_direct_reference(spec):
        return None
    match = REQUIREMENT_NAME_REGEX.match(spec)
    if not match:
        return None
    name, extras = match.group(1), match.group(2) or ""
    if extras:
        extras_list = [x.strip() for x in extras[1:-1].split(",") if x.strip()]
        extras = "[%s]" % ",".join(extras_list) if extras_list else ""
    return name, extras


def _split_pip_args(args: List[str], command: str) -> List[str]:
    """
    Get requirements passed to a pip command, skipping options and their values.

    pip's own parser is used, so options with values (`-i URL`, `-c FILE`,
    `--proxy=...`) are handled for every pip version. Editable requirements
    (`-e PATH`) are returned too.

    :param args: arguments of the pip command.
    :param command: pip command, e.g. `install`.
    :return: requirements as passed by the user.
    """
    try:
        from pip._internal.commands import create_command

        options, positional = create_command(command).parse_args(list(args))
        return list(positional) + list(getattr(options, "editables", None) or [])
    except (Exception, SystemExit):
        # Unknown pip layout: fall back to skipping anything that looks like
        # an option. Values of options may then be mistaken for packages.
        return [arg for arg in args if not arg.startswith("-")]


def parse_packages_names(args: Iterable, command: str = "install") -> List[str]:
    """
    Parse requirements from pip command arguments.

    Version specifiers are dropped and extras are kept: `requests[socks]>=2`
    becomes `requests[socks]`. Direct references (URLs, paths) are returned
    as is, except for `.` (the current project).

    :param args: arguments.
    :param command: pip command the arguments belong to.
    :return: list of package names.
    """
    packages_names = []
    for spec in _split_pip_args(list(args), command):
        spec = spec.strip()
        if not spec or spec == ".":
            continue
        split = split_requirement(spec)
        packages_names.append("".join(split) if split else spec)
    return packages_names


def get_requirement_key(requirement: str) -> Optional[str]:
    """
    Get a key identifying the project a requirement line refers to.

    :param requirement: requirement (or requirements.txt line).
    :return: canonical project name; None for direct references.
    """
    split = split_requirement(requirement)
    return canonicalize_name(split[0]) if split else None


def parse_requirements_txt(path: str) -> OrderedDict:
    """
    Parse requirements.txt file.

    :param path: path to requirements.txt.
    :return: mapping of package names to package versions.
    """
    requirements_dict = OrderedDict()
    for requirement in read_text_file(path).text.split("\n"):
        requirement = requirement.strip()
        if requirement.startswith("#") or requirement == "":
            continue
        requirement_split = requirement.split("==")
        if len(requirement_split) == 2 and split_requirement(requirement):
            name, version = (x.strip() for x in requirement_split)
            requirements_dict[name] = version
        else:
            # Unpinned, other specifiers, URLs, options, ...: kept verbatim.
            requirements_dict[requirement] = None
    return requirements_dict


__all__ = [
    "canonicalize_name",
    "get_packages_info",
    "get_requirement_key",
    "is_direct_reference",
    "split_requirement",
    "parse_packages_names",
    "parse_requirements_txt",
]
