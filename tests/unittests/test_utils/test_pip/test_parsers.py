import os.path

import pytest
from types import SimpleNamespace
from unittest.mock import patch, Mock

from requirements_txt.utils.pip.parsers import (
    canonicalize_name,
    get_packages_info,
    get_requirement_key,
    split_requirement,
    parse_packages_names,
    parse_requirements_txt,
)


class TestCanonicalizeName:
    def test_canonicalize_name(self):
        assert canonicalize_name("PyYAML") == "pyyaml"
        assert canonicalize_name("zope.interface") == "zope-interface"
        assert canonicalize_name("Foo__Bar-.baz") == "foo-bar-baz"


def _distribution(name: str, version: str) -> SimpleNamespace:
    return SimpleNamespace(metadata={"Name": name}, version=version)


class TestGetPackagesInfo:
    @patch("requirements_txt.utils.pip.parsers.importlib.metadata.distributions")
    def test_get_packages_info_1(self, distributions_mock: Mock):
        distributions_mock.return_value = [_distribution("appdata", "1.0.0")]
        packages_info = get_packages_info(["appdata"])
        assert packages_info == {"appdata": "1.0.0"}

    @patch("requirements_txt.utils.pip.parsers.importlib.metadata.distributions")
    def test_get_packages_info_name_normalization(self, distributions_mock: Mock):
        # The metadata name is reported, whatever spelling was requested.
        distributions_mock.return_value = [_distribution("PyYAML", "6.0")]
        packages_info = get_packages_info(["pyyaml"])
        assert packages_info == {"PyYAML": "6.0"}

    @patch("requirements_txt.utils.pip.parsers.importlib.metadata.distributions")
    def test_get_packages_info_missing_and_order(self, distributions_mock: Mock):
        distributions_mock.return_value = [
            _distribution("b", "2.0"),
            _distribution("a", "1.0"),
        ]
        packages_info = get_packages_info(["a", "missing", "b"])
        assert list(packages_info.items()) == [("a", "1.0"), ("b", "2.0")]

    @patch("requirements_txt.utils.pip.parsers.importlib.metadata.distributions")
    def test_get_packages_info_first_match_wins(self, distributions_mock: Mock):
        distributions_mock.return_value = [
            _distribution("appdata", "2.0"),
            _distribution("appdata", "1.0"),
        ]
        assert get_packages_info(["appdata"]) == {"appdata": "2.0"}

    def test_get_packages_info_real_environment(self):
        # pytest is installed in the test environment.
        packages_info = get_packages_info(["PYTEST", "surely-not-installed-xyz"])
        assert list(packages_info) == ["pytest"]


class TestParsePackagesNames:
    def test_parse_packages_names_1(self):
        args = ["appdata==1.0.0", "-r", "requirements.txt"]
        packages_names = parse_packages_names(args)
        # The value of `-r` is not a package.
        assert packages_names == ["appdata"]

    def test_parse_packages_names_2(self):
        args = ["."]
        packages_names = parse_packages_names(args)
        # requirements.txt will be filtered while searching installed package
        assert packages_names == []

    def test_parse_packages_names_3(self):
        args = ["appdata==12.3.2", "other_module", "another==5.2.1"]
        packages_names = parse_packages_names(args)
        # requirements.txt will be filtered while searching installed package
        assert packages_names == ["appdata", "other_module", "another"]


class TestParsePackagesNamesPipOptions:
    @pytest.mark.parametrize(
        "args, expected",
        [
            # Options with values (#4): the value is not a package.
            (["-i", "https://example.org/simple", "appdata"], ["appdata"]),
            (["--index-url=https://example.org/simple", "appdata"], ["appdata"]),
            (["--proxy", "host:3128", "-c", "constraints.txt", "a"], ["a"]),
            (["--no-deps", "-U", "appdata", "--target", "/tmp/x"], ["appdata"]),
            # Extras (#10) are kept, version specifiers are dropped.
            (["requests[socks]"], ["requests[socks]"]),
            (["requests[socks, security]>=2.0"], ["requests[socks,security]"]),
            (["Django>=4,<5"], ["Django"]),
            (["zope.interface~=5.0"], ["zope.interface"]),
            # Editables and direct references are returned as is.
            (["-e", "./local_pkg"], ["./local_pkg"]),
            (["-e", "."], []),
            (["git+https://github.com/a/b.git"], ["git+https://github.com/a/b.git"]),
            (["name @ https://x/y.whl"], ["name @ https://x/y.whl"]),
        ],
    )
    def test_install(self, args, expected):
        assert parse_packages_names(args) == expected

    def test_uninstall(self):
        args = ["-y", "--root-user-action", "ignore", "PyYAML"]
        assert parse_packages_names(args, command="uninstall") == ["PyYAML"]


class TestSplitRequirement:
    @pytest.mark.parametrize(
        "spec, expected",
        [
            ("requests", ("requests", "")),
            ("requests[socks]==2.0", ("requests", "[socks]")),
            ("requests [ socks , b ] >= 2", ("requests", "[socks,b]")),
            ("foo; python_version < '3.9'", ("foo", "")),
            ("git+https://github.com/a/b.git", None),
            ("./local", None),
            ("name @ https://x/y.whl", None),
            ("-r other.txt", None),
        ],
    )
    def test_split_requirement(self, spec, expected):
        assert split_requirement(spec) == expected

    def test_get_requirement_key(self):
        assert get_requirement_key("Requests[socks]>=2") == "requests"
        assert get_requirement_key("./local") is None


class TestParseRequirementsTxt:
    def test_parse_requirements_txt_keeps_unpinned_lines_verbatim(self, temp_dir: str):
        requirements_txt_path = os.path.join(temp_dir, "requirements.txt-temp")
        with open(requirements_txt_path, "w+") as f:
            f.writelines(["foo>=1.0\n", "bar[x]==2.0\n", "--index-url https://x\n"])
        requirements_txt_data = parse_requirements_txt(requirements_txt_path)
        assert dict(requirements_txt_data) == {
            "foo>=1.0": None,
            "bar[x]": "2.0",
            "--index-url https://x": None,
        }

    def test_parse_requirements_txt_1(self, temp_dir: str):
        requirements_txt_path = os.path.join(temp_dir, "requirements.txt-temp")
        with open(requirements_txt_path, "w+") as f:
            f.writelines(
                [
                    "appdata==1.0.2\n",
                ]
            )
        requirements_txt_data = parse_requirements_txt(requirements_txt_path)
        assert len(requirements_txt_data) == 1
        assert requirements_txt_data["appdata"] == "1.0.2"

    def test_parse_requirements_txt_2(self, temp_dir: str):
        requirements_txt_path = os.path.join(temp_dir, "requirements.txt-temp")
        with open(requirements_txt_path, "w+") as f:
            f.writelines(
                [
                    "appdata\n",
                ]
            )
        requirements_txt_data = parse_requirements_txt(requirements_txt_path)
        assert len(requirements_txt_data) == 1
        assert requirements_txt_data["appdata"] is None

    def test_parse_requirements_txt_3(self, temp_dir: str):
        requirements_txt_path = os.path.join(temp_dir, "requirements.txt-temp")
        with open(requirements_txt_path, "w+") as f:
            f.writelines(
                [
                    "appdata",
                ]
            )
        requirements_txt_data = parse_requirements_txt(requirements_txt_path)
        assert len(requirements_txt_data) == 1
        assert requirements_txt_data["appdata"] is None

    def test_parse_requirements_txt_4(self, temp_dir: str):
        requirements_txt_path = os.path.join(temp_dir, "requirements.txt-temp")
        with open(requirements_txt_path, "w+") as f:
            f.writelines(["# some comment\n", "appdata==1.0.2\n", "another_module\n"])
        requirements_txt_data = parse_requirements_txt(requirements_txt_path)
        assert len(requirements_txt_data) == 2
        assert requirements_txt_data["appdata"] == "1.0.2"
        assert requirements_txt_data["another_module"] is None
