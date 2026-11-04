import codecs

import pytest

from requirements_txt.utils.files import (
    detect_encoding,
    read_text_file,
    write_text_file,
)

CONTENT = "appdata==2.2.1\n# café\nclick==8.0.3\n"


@pytest.mark.parametrize(
    "encoding, bom",
    [
        ("utf-8", b""),
        ("utf-8-sig", codecs.BOM_UTF8),
        ("utf-16", codecs.BOM_UTF16_LE),  # what PowerShell `>` writes
        ("utf-16-be", codecs.BOM_UTF16_BE),
        ("utf-32", codecs.BOM_UTF32_LE),
    ],
)
def test_read_and_write_preserve_encoding(tmp_path, encoding, bom):
    path = str(tmp_path / "requirements.txt")
    data = CONTENT.encode(encoding)
    if encoding == "utf-16-be":
        data = codecs.BOM_UTF16_BE + data
    if encoding == "utf-16":
        # Python writes the native-order BOM; make the fixture deterministic.
        data = codecs.BOM_UTF16_LE + CONTENT.encode("utf-16-le")
    with open(path, "wb") as f:
        f.write(data)

    text_file = read_text_file(path)
    assert text_file.text == CONTENT
    assert data.startswith(bom)

    write_text_file(path, text_file.text, text_file.encoding, text_file.newline)
    with open(path, "rb") as f:
        written = f.read()
    # Same encoding family (and a BOM if there was one); UTF-16/32 may be
    # written back in native byte order, which every reader handles.
    assert detect_encoding(written) == text_file.encoding
    assert bool(bom) == (detect_encoding(written) != "utf-8")
    assert read_text_file(path).text == CONTENT


def test_crlf_line_endings_are_preserved(tmp_path):
    path = str(tmp_path / "requirements.txt")
    with open(path, "wb") as f:
        f.write(CONTENT.replace("\n", "\r\n").encode("utf-16"))

    text_file = read_text_file(path)
    assert text_file.text == CONTENT
    assert text_file.newline == "\r\n"

    write_text_file(path, text_file.text, text_file.encoding, text_file.newline)
    with open(path, "rb") as f:
        assert f.read().decode("utf-16") == CONTENT.replace("\n", "\r\n")


def test_legacy_8_bit_encoding_does_not_crash():
    # Not valid UTF-8: falls back to the locale encoding or latin-1.
    assert detect_encoding("# caf\xe9\n".encode("cp1252")) != "utf-8"


def test_empty_file_is_utf_8():
    assert detect_encoding(b"") == "utf-8"
