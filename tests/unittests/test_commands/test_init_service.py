import sys
from unittest.mock import patch

import pytest

from requirements_txt.commands.init.service import (
    InitError,
    _run_step,
    install_for_venv,
)


class TestRunStep:
    def test_success(self):
        _run_step([sys.executable, "-c", "pass"], verbose=False)

    def test_failure_includes_exit_code_and_output(self):
        with pytest.raises(InitError) as exc_info:
            _run_step(
                [sys.executable, "-c", "import sys; print('boom'); sys.exit(3)"],
                verbose=False,
            )
        message = exc_info.value.format_message()
        assert "exited with code 3" in message
        assert "boom" in message

    def test_failure_without_output_suggests_verbose(self):
        with pytest.raises(InitError) as exc_info:
            _run_step([sys.executable, "-c", "import sys; sys.exit(1)"], verbose=False)
        assert "--verbose" in exc_info.value.format_message()


class TestInstallForVenv:
    @patch("requirements_txt.commands.init.service.find_virtualenv")
    def test_missing_virtualenv_is_an_error(self, find_virtualenv_mock):
        find_virtualenv_mock.return_value = None
        with pytest.raises(InitError):
            install_for_venv()
