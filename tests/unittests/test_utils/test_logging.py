import sys

from colored import fg

from requirements_txt.utils.logging import (
    set_verbose,
    logger_handler,
    show_all_done_message,
)


class TestSetVerbose:
    def test_set_verbose_1(self):
        assert logger_handler.terminator == ""
        try:
            set_verbose(True)
            assert logger_handler.terminator == "\n"
        finally:
            logger_handler.terminator = ""

    def test_set_verbose_2(self):
        logger_handler.terminator = "\n"
        try:
            set_verbose(False)
            assert logger_handler.terminator == ""
        finally:
            logger_handler.terminator = ""


class TestShowAllDoneMessage:
    def test_not_sourced_shows_activate_command(self, capfd, monkeypatch):
        monkeypatch.delenv("REX_SOURCED", raising=False)
        show_all_done_message("./venv")
        out, _ = capfd.readouterr()
        assert "All done! Your virtualenv project is ready." in out
        assert "Virtual environment  venv" in out
        assert "source venv/bin/activate" in out
        assert "requirements.txt is updated automatically" in out
        # Typo in the previous message.
        assert "codding" not in out

    def test_sourced_does_not_ask_to_activate(self, capfd, monkeypatch):
        monkeypatch.setenv("REX_SOURCED", "1")
        show_all_done_message("./venv")
        out, _ = capfd.readouterr()
        assert "The virtual environment is activated." in out
        assert "source venv/bin/activate" not in out

    def test_no_escape_codes_when_not_a_tty(self, capfd, monkeypatch):
        # capfd output is not a terminal.
        show_all_done_message("./venv")
        out, _ = capfd.readouterr()
        assert "\x1b[" not in out

    def test_colors_on_a_tty(self, monkeypatch, capsys):
        monkeypatch.delenv("NO_COLOR", raising=False)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        show_all_done_message("./venv")
        out, _ = capsys.readouterr()
        assert fg("green") in out

    def test_no_color_env(self, monkeypatch, capsys):
        monkeypatch.setenv("NO_COLOR", "1")
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
        show_all_done_message("./venv")
        out, _ = capsys.readouterr()
        assert "\x1b[" not in out
