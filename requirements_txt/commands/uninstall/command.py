import importlib.metadata

import click

from requirements_txt.commands.cli import cli
from requirements_txt.commands.uninstall.service import (
    uninstall as uninstall_from_pip,
)


def _get_distribution_name() -> str:
    # Published as `rex`, `to-requirements.txt` and `requirements-txt`.
    try:
        names = importlib.metadata.packages_distributions().get("requirements_txt")
    except AttributeError:  # Python < 3.10
        names = None
    return names[0] if names else "rex"


@cli.command()
def uninstall():
    """Restore pip scripts patched by to-requirements.txt."""
    restored = uninstall_from_pip()
    if restored:
        click.echo(
            "requirements.txt synchronization is disabled for these pip scripts.\n"
            f"To remove the package itself, run: pip uninstall {_get_distribution_name()}"
        )
    else:
        click.echo("No pip scripts patched by to-requirements.txt were found.")


__all__ = [
    "uninstall",
]
