import os
import subprocess
import sys

import requirements_txt

PACKAGE_DIR = os.path.dirname(requirements_txt.__file__)
NEW_PIP_TEMPLATE = os.path.join(PACKAGE_DIR, "static", "new_pip.py")


def _run_patched_pip(tmp_path, *args):
    with open(NEW_PIP_TEMPLATE) as template:
        script = template.read().format(python_path=sys.executable)
    script_path = tmp_path / "pip"
    script_path.write_text(script)
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        # Make the package under test importable from the patched script.
        env={**os.environ, "PYTHONPATH": os.path.dirname(PACKAGE_DIR)},
    )


class TestNoSave:
    def test_no_save_is_not_passed_to_pip_and_skips_the_hook(
        self, tmp_path, monkeypatch
    ):
        project = tmp_path / "project"
        project.mkdir()
        requirements_txt_path = project / "requirements.txt"
        requirements_txt_path.write_text("surely-not-installed-xyz==1.0\n")
        monkeypatch.chdir(project)

        result = _run_patched_pip(
            tmp_path, "uninstall", "-y", "--no-save", "surely-not-installed-xyz"
        )

        # pip would fail with "no such option: --no-save" if it saw the flag.
        assert result.returncode == 0, result.stderr
        assert "no such option" not in result.stderr
        assert "Traceback" not in result.stderr
        assert requirements_txt_path.read_text() == "surely-not-installed-xyz==1.0\n"

    def test_no_save_is_listed_in_help(self, tmp_path):
        result = _run_patched_pip(tmp_path, "install", "--help")
        assert result.returncode == 0
        assert "REX Options:" in result.stdout
        assert "--no-save" in result.stdout

    def test_other_commands_are_not_changed(self, tmp_path):
        result = _run_patched_pip(tmp_path, "list", "--no-save")
        # Not a REX option for `pip list`: pip reports it as usual.
        assert result.returncode != 0
        assert "no such option: --no-save" in result.stderr
