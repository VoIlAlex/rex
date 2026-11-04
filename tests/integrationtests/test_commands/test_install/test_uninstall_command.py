import os
import subprocess
import sys
from unittest.mock import patch, Mock

from click.testing import CliRunner

from requirements_txt.commands import cli
from requirements_txt.utils.override import is_patched, override_pip

STOCK_PIP = """#!/usr/bin/python3
# stock pip
"""


def _write(path, content):
    with open(path, "w") as f:
        f.write(content)


class TestCommandUninstall:
    @patch("requirements_txt.commands.uninstall.service.get_pip_path")
    def test_restores_patched_pip_scripts(self, get_pip_path_mock: Mock, tmp_path):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        python_path = sys.executable
        for name in ["pip", "pip3", "pip3.13"]:
            override_pip(str(bin_dir / name), python_path)
        _write(str(bin_dir / "pip-compile"), STOCK_PIP)  # not patched
        get_pip_path_mock.side_effect = [
            (str(bin_dir / "pip"), "python3"),
            (str(bin_dir / "pip3"), "python3"),
        ]

        result = CliRunner().invoke(cli, ["uninstall"])

        assert result.exit_code == 0, result.output
        assert "pip uninstall " in result.output
        for name in ["pip", "pip3", "pip3.13"]:
            path = str(bin_dir / name)
            assert not is_patched(path)
            with open(path) as f:
                content = f.read()
            assert content.startswith(f"#!{python_path}\n")
            assert "from pip._internal.cli.main import main" in content
        with open(str(bin_dir / "pip-compile")) as f:
            assert f.read() == STOCK_PIP

    @patch("requirements_txt.commands.uninstall.service.get_pip_path")
    def test_restored_script_runs_pip(self, get_pip_path_mock: Mock, tmp_path):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        override_pip(str(bin_dir / "pip"), sys.executable)
        get_pip_path_mock.side_effect = [
            (str(bin_dir / "pip"), "python3"),
            (None, None),
        ]

        assert CliRunner().invoke(cli, ["uninstall"]).exit_code == 0

        output = subprocess.check_output(
            [sys.executable, str(bin_dir / "pip"), "--version"], text=True
        )
        assert output.startswith("pip ")

    @patch("requirements_txt.commands.uninstall.service.get_pip_path")
    def test_nothing_to_restore(self, get_pip_path_mock: Mock, tmp_path):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _write(str(bin_dir / "pip"), STOCK_PIP)
        get_pip_path_mock.side_effect = [
            (str(bin_dir / "pip"), "python3"),
            (None, None),
        ]

        result = CliRunner().invoke(cli, ["uninstall"])

        assert result.exit_code == 0
        assert "No pip scripts patched" in result.output
        with open(str(bin_dir / "pip")) as f:
            assert f.read() == STOCK_PIP

    @patch("requirements_txt.commands.uninstall.service.get_pip_path")
    def test_unrestorable_scripts_are_reported(
        self, get_pip_path_mock: Mock, tmp_path, caplog
    ):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        override_pip(str(bin_dir / "pip"), sys.executable)
        override_pip(str(bin_dir / "pip-compile"), sys.executable)
        get_pip_path_mock.side_effect = [
            (str(bin_dir / "pip"), "python3"),
            (None, None),
        ]

        result = CliRunner().invoke(cli, ["uninstall"])

        assert result.exit_code == 0
        assert is_patched(str(bin_dir / "pip-compile"))
        assert not is_patched(str(bin_dir / "pip"))
        assert "pip-compile" in caplog.text
