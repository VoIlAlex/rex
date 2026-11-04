"""
Read and write requirements.txt files in whatever encoding they were saved.

On Windows, PowerShell (`pip freeze > requirements.txt`) and some editors
save text as UTF-16 or as UTF-8 with a BOM, often with CRLF line endings.
"""
import codecs
import locale
from typing import NamedTuple

# This module is used by the patched pip script after pip has installed
# packages; recent pip warns about imports done at that point, so load the
# codecs we may need up front.
import encodings.latin_1  # noqa: F401
import encodings.utf_16  # noqa: F401
import encodings.utf_32  # noqa: F401
import encodings.utf_8_sig  # noqa: F401

DEFAULT_ENCODING = "utf-8"

# Longest BOMs first: the UTF-32 LE BOM starts with the UTF-16 LE BOM.
BOMS = (
    (codecs.BOM_UTF32_LE, "utf-32"),
    (codecs.BOM_UTF32_BE, "utf-32"),
    (codecs.BOM_UTF8, "utf-8-sig"),
    (codecs.BOM_UTF16_LE, "utf-16"),
    (codecs.BOM_UTF16_BE, "utf-16"),
)


class TextFile(NamedTuple):
    text: str
    encoding: str
    newline: str


def detect_encoding(data: bytes) -> str:
    """
    Detect the encoding of a text file's content.

    :param data: raw file content.
    :return: encoding usable with `open(..., encoding=...)`.
    """
    for bom, encoding in BOMS:
        if data.startswith(bom):
            return encoding
    for encoding in (DEFAULT_ENCODING, locale.getpreferredencoding(False)):
        try:
            data.decode(encoding)
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    # Never fails: every byte is a valid latin-1 character.
    return "latin-1"


def read_text_file(path: str) -> TextFile:
    """
    Read a text file, detecting its encoding and line endings.

    :param path: path to the file.
    :return: text with `\\n` line endings, encoding and original newline.
    """
    with open(path, "rb") as f:
        data = f.read()
    encoding = detect_encoding(data)
    text = data.decode(encoding)
    newline = "\r\n" if "\r\n" in text else "\n"
    return TextFile(text.replace("\r\n", "\n"), encoding, newline)


def write_text_file(
    path: str,
    text: str,
    encoding: str = DEFAULT_ENCODING,
    newline: str = "\n",
):
    """
    Write a text file using the given encoding and line endings.

    :param path: path to the file.
    :param text: text with `\\n` line endings.
    :param encoding: encoding to write with (BOM encodings add the BOM).
    :param newline: line ending to write.
    """
    with open(path, "w", encoding=encoding, newline=newline) as f:
        f.write(text)


__all__ = [
    "TextFile",
    "detect_encoding",
    "read_text_file",
    "write_text_file",
]
