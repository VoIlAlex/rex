import os
import sys

import pytest

from requirements_txt.utils.pip.selfupdate import (
    is_patched,
    is_pip_self_install,
    repatch_pip_scripts,
)

STOCK_PIP_SCRIPT = """#!/venv/bin/python
import re
import sys
from pip._internal.cli.main import main
if __name__ == '__main__':
    sys.exit(main())
"""


class TestIsPipSelfInstall:
    @pytest.mark.parametrize(
        "args",
        [
            ["pip"],
            ["-U", "pip"],
            ["--upgrade", "pip", "setuptools"],
            ["pip==24.0"],
            ["PIP>=23"],
            ["pip[foo]"],
        ],
    )
    def test_pip_requested(self, args):
        assert is_pip_self_install(args)

    @pytest.mark.parametrize(
        "args",
        [
            [],
            ["pip-tools"],
            ["pipx"],
            ["pipenv==2023.1"],
            ["-r", "requirements.txt"],
            ["appdata", "--no-pip-option"],
        ],
    )
    def test_pip_not_requested(self, args):
        assert not is_pip_self_install(args)


class TestRepatchPipScripts:
    def _write(self, path, content):
        with open(path, "w") as f:
            f.write(content)

    def test_repatches_only_unpatched_pip_scripts(self, tmp_path):
        bin_dir = str(tmp_path)
        for name in ["pip", "pip-3.13", "pip3", "pip3.13", "pip-compile", "pipx", "python"]:
            self._write(os.path.join(bin_dir, name), STOCK_PIP_SCRIPT)
        # Already patched: must be left untouched.
        patched_content = "#!/venv/bin/python\nimport requirements_txt\n"
        self._write(os.path.join(bin_dir, "pip3.12"), patched_content)

        repatched = repatch_pip_scripts(bin_dir, sys.executable)

        assert repatched == ["pip", "pip-3.13", "pip3", "pip3.13"]
        for name in repatched:
            path = os.path.join(bin_dir, name)
            assert is_patched(path)
            with open(path) as f:
                assert f.readline() == f"#!{sys.executable}\n"
        for name in ["pip-compile", "pipx", "python"]:
            assert not is_patched(os.path.join(bin_dir, name))
        with open(os.path.join(bin_dir, "pip3.12")) as f:
            assert f.read() == patched_content

    def test_nothing_to_repatch(self, tmp_path):
        assert repatch_pip_scripts(str(tmp_path), sys.executable) == []
