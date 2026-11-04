import os.path
from types import SimpleNamespace
from unittest.mock import patch, Mock

from requirements_txt.utils.pip.parsers import (
    canonicalize_name,
    get_packages_info,
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
        # requirements.txt will be filtered while searching installed package
        assert packages_names == ["appdata", "requirements.txt"]

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


class TestParseRequirementsTxt:
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
