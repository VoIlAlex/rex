import os
import subprocess
import sys

import requirements_txt

PACKAGE_DIR = os.path.dirname(requirements_txt.__file__)
NEW_PIP_TEMPLATE = os.path.join(PACKAGE_DIR, "static", "new_pip.py")


def _write_patched_pip(directory: str) -> str:
    with open(NEW_PIP_TEMPLATE) as template:
        script = template.read().format(python_path=sys.executable)
    script_path = os.path.join(directory, "pip")
    with open(script_path, "w") as f:
        f.write(script)
    return script_path


def _run_pip(script_path: str, *args: str, env: dict = None):
    return subprocess.run(
        [sys.executable, script_path, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        # Make the package under test importable from the patched script.
        env={
            **os.environ,
            "PYTHONPATH": os.path.dirname(PACKAGE_DIR),
            **(env or {}),
        },
    )


class TestNewPipErrorReporting:
    def test_hook_failure_is_reported_and_keeps_exit_code(self, tmp_path, monkeypatch):
        script_path = _write_patched_pip(str(tmp_path))
        project = tmp_path / "project"
        project.mkdir()
        # A directory where the file should be makes the hook fail to read it.
        (project / "requirements.txt").mkdir()

        monkeypatch.chdir(project)
        # Uninstalling a missing package is a no-op success for pip.
        result = _run_pip(script_path, "uninstall", "-y", "surely-not-installed-xyz")

        assert result.returncode == 0
        assert "rex: failed to update requirements.txt" in result.stderr
        assert "REX_DEBUG=1" in result.stderr

    def test_rex_debug_prints_traceback(self, tmp_path, monkeypatch):
        script_path = _write_patched_pip(str(tmp_path))
        project = tmp_path / "project"
        project.mkdir()
        (project / "requirements.txt").mkdir()

        monkeypatch.chdir(project)
        result = _run_pip(
            script_path,
            "uninstall",
            "-y",
            "surely-not-installed-xyz",
            env={"REX_DEBUG": "1"},
        )

        assert result.returncode == 0
        assert "Traceback (most recent call last)" in result.stderr

    def test_pip_exit_code_is_preserved_on_pip_failure(self, tmp_path):
        script_path = _write_patched_pip(str(tmp_path))
        result = _run_pip(script_path, "install", "--definitely-not-a-pip-flag")
        assert result.returncode != 0
        assert "rex:" not in result.stderr
