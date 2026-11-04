import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock, Mock, call, file_spec

from requirements_txt.utils.override import override_pip


class TestOverridePip:
    @patch("builtins.open", new_callable=mock_open)
    def test_override_pip_1(self, mock_open: Mock):
        mock_open.return_value = MagicMock(spec=file_spec)
        override_pip("/path/to/pip", "/path/to/python")
        new_pip_path = os.path.join(
            Path(__file__).parents[3].absolute(),
            "requirements_txt",
            "static",
            "new_pip.py",
        )
        mock_open.assert_has_calls(
            [call("/path/to/pip", "w+"), call(new_pip_path)], any_order=True
        )

        mock_open.return_value.__enter__.return_value.write.assert_called_once_with(
            mock_open.return_value.__enter__.return_value.read.return_value.format.return_value
        )


class TestRestorePip:
    def test_not_patched_is_left_alone(self, tmp_path):
        from requirements_txt.utils.override import restore_pip

        path = tmp_path / "pip"
        path.write_text("#!/usr/bin/python3\nstock\n")
        assert restore_pip(str(path)) is False
        assert path.read_text() == "#!/usr/bin/python3\nstock\n"

    def test_shebang_python_is_kept(self, tmp_path):
        from requirements_txt.utils.override import (
            get_shebang_python,
            is_patched,
            override_pip as real_override_pip,
            restore_pip,
        )

        path = str(tmp_path / "pip")
        real_override_pip(path, "/venv/bin/python")
        assert is_patched(path)
        assert restore_pip(path) is True
        assert not is_patched(path)
        assert get_shebang_python(path) == "/venv/bin/python"
