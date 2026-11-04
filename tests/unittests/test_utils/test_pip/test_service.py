import os
from unittest.mock import patch, Mock

from requirements_txt.utils.pip import (
    add_installed_packages_to_requirements_txt,
    remove_uninstalled_packages_from_requirements_txt,
)


@patch("requirements_txt.utils.pip.service.parse_packages_names")
@patch("requirements_txt.utils.pip.service.get_packages_info")
@patch("requirements_txt.utils.pip.service.check_git_only_restriction")
@patch("requirements_txt.utils.pip.service.get_requirements_txt_path")
@patch("requirements_txt.utils.pip.service.parse_requirements_txt")
class TestAddInstalledPackagesToRequirementsTxt:
    def test_add_installed_packages_to_requirements_txt_1(
        self,
        parse_requirements_txt_mock: Mock,
        get_requirements_txt_path_mock: Mock,
        check_git_only_restriction_mock: Mock,
        get_packages_info_mock: Mock,
        parse_packages_names_mock: Mock,
        temp_dir,
    ):
        requirements_txt_path_exp = os.path.join(os.getcwd(), "requirements.txt")
        parse_packages_names_mock.return_value = ["appdata"]
        get_packages_info_mock.return_value = {"appdata": "1.0.0"}
        check_git_only_restriction_mock.return_value = True
        get_requirements_txt_path_mock.return_value = (requirements_txt_path_exp, False)
        parse_requirements_txt_mock.return_value = {}

        add_installed_packages_to_requirements_txt(["appdata==1.0.0"])

        with open(requirements_txt_path_exp, "r") as f:
            assert f.read() == "appdata==1.0.0\n"

        parse_packages_names_mock.assert_called_once_with(["appdata==1.0.0"])
        get_packages_info_mock.assert_called_once_with(["appdata"])
        check_git_only_restriction_mock.assert_called_once_with()
        get_requirements_txt_path_mock.assert_called_once_with()
        parse_requirements_txt_mock.assert_called_once_with(requirements_txt_path_exp)

    def test_add_installed_packages_to_requirements_txt_2(
        self,
        parse_requirements_txt_mock: Mock,
        get_requirements_txt_path_mock: Mock,
        check_git_only_restriction_mock: Mock,
        get_packages_info_mock: Mock,
        parse_packages_names_mock: Mock,
        temp_dir,
    ):
        parse_packages_names_mock.return_value = ["appdata"]
        get_packages_info_mock.return_value = {"appdata": "1.0.0"}
        check_git_only_restriction_mock.return_value = False

        add_installed_packages_to_requirements_txt(["appdata==1.0.0"])

        requirements_txt_path_exp = os.path.join(os.getcwd(), "requirements.txt")
        assert not os.path.exists(requirements_txt_path_exp)

        parse_packages_names_mock.assert_called_once_with(["appdata==1.0.0"])
        get_packages_info_mock.assert_called_once_with(["appdata"])
        check_git_only_restriction_mock.assert_called_once_with()
        get_requirements_txt_path_mock.assert_not_called()
        parse_requirements_txt_mock.assert_not_called()

    def test_add_installed_packages_to_requirements_txt_3(
        self,
        parse_requirements_txt_mock: Mock,
        get_requirements_txt_path_mock: Mock,
        check_git_only_restriction_mock: Mock,
        get_packages_info_mock: Mock,
        parse_packages_names_mock: Mock,
        temp_dir,
    ):
        parse_packages_names_mock.return_value = ["appdata"]
        get_packages_info_mock.return_value = {"appdata": "1.0.0"}
        check_git_only_restriction_mock.return_value = True
        get_requirements_txt_path_mock.return_value = (None, False)

        add_installed_packages_to_requirements_txt(["appdata==1.0.0"])

        requirements_txt_path_exp = os.path.join(os.getcwd(), "requirements.txt")
        assert not os.path.exists(requirements_txt_path_exp)

        parse_packages_names_mock.assert_called_once_with(["appdata==1.0.0"])
        get_packages_info_mock.assert_called_once_with(["appdata"])
        check_git_only_restriction_mock.assert_called_once_with()
        get_requirements_txt_path_mock.assert_called_once_with()
        parse_requirements_txt_mock.assert_not_called()


@patch("requirements_txt.utils.pip.service.parse_packages_names")
@patch("requirements_txt.utils.pip.service.get_packages_info")
@patch("requirements_txt.utils.pip.service.check_git_only_restriction")
@patch("requirements_txt.utils.pip.service.get_requirements_txt_path")
@patch("requirements_txt.utils.pip.service.parse_requirements_txt")
class TestRemoveUninstalledPackagesFromRequirementsTxt:
    def test_remove_uninstalled_packages_from_requirements_txt_1(
        self,
        parse_requirements_txt_mock: Mock,
        get_requirements_txt_path_mock: Mock,
        check_git_only_restriction_mock: Mock,
        get_packages_info_mock: Mock,
        parse_packages_names_mock: Mock,
        temp_dir,
    ):
        requirements_txt_path_exp = os.path.join(os.getcwd(), "requirements.txt")
        with open(requirements_txt_path_exp, "w+") as f:
            f.writelines(["appdata==0.2.1\n", "something==2.1.1\n", "other==2.1.5\n"])

        parse_packages_names_mock.return_value = ["something"]
        get_packages_info_mock.return_value = {}
        check_git_only_restriction_mock.return_value = True
        get_requirements_txt_path_mock.return_value = (requirements_txt_path_exp, False)
        parse_requirements_txt_mock.return_value = {
            "appdata": "0.2.1",
            "something": "2.1.1",
            "other": "2.1.5",
        }

        remove_uninstalled_packages_from_requirements_txt(["something"])

        with open(requirements_txt_path_exp, "r") as f:
            assert f.read() == "appdata==0.2.1\nother==2.1.5\n"

        parse_packages_names_mock.assert_called_once_with(["something"])
        get_packages_info_mock.assert_called_once_with(["something"])
        check_git_only_restriction_mock.assert_called_once_with()
        get_requirements_txt_path_mock.assert_called_once_with(try_create=False)
        parse_requirements_txt_mock.assert_called_once_with(requirements_txt_path_exp)

    def test_remove_uninstalled_packages_from_requirements_txt_2(
        self,
        parse_requirements_txt_mock: Mock,
        get_requirements_txt_path_mock: Mock,
        check_git_only_restriction_mock: Mock,
        get_packages_info_mock: Mock,
        parse_packages_names_mock: Mock,
        temp_dir,
    ):
        parse_packages_names_mock.return_value = ["something"]
        get_packages_info_mock.return_value = {}
        check_git_only_restriction_mock.return_value = False

        remove_uninstalled_packages_from_requirements_txt(["something"])

        parse_packages_names_mock.assert_called_once_with(["something"])
        get_packages_info_mock.assert_called_once_with(["something"])
        check_git_only_restriction_mock.assert_called_once_with()
        get_requirements_txt_path_mock.assert_not_called()
        parse_requirements_txt_mock.assert_not_called()

    def test_remove_uninstalled_packages_from_requirements_txt_3(
        self,
        parse_requirements_txt_mock: Mock,
        get_requirements_txt_path_mock: Mock,
        check_git_only_restriction_mock: Mock,
        get_packages_info_mock: Mock,
        parse_packages_names_mock: Mock,
        temp_dir,
    ):
        parse_packages_names_mock.return_value = ["something"]
        get_packages_info_mock.return_value = {}
        check_git_only_restriction_mock.return_value = True
        get_requirements_txt_path_mock.return_value = (None, False)

        remove_uninstalled_packages_from_requirements_txt(["something"])

        parse_packages_names_mock.assert_called_once_with(["something"])
        get_packages_info_mock.assert_called_once_with(["something"])
        check_git_only_restriction_mock.assert_called_once_with()
        get_requirements_txt_path_mock.assert_called_once_with(try_create=False)
        parse_requirements_txt_mock.assert_not_called()

    def test_remove_uninstalled_packages_name_normalization(
        self,
        parse_requirements_txt_mock: Mock,
        get_requirements_txt_path_mock: Mock,
        check_git_only_restriction_mock: Mock,
        get_packages_info_mock: Mock,
        parse_packages_names_mock: Mock,
        temp_dir,
    ):
        # `pip uninstall pyyaml` must remove the `PyYAML==...` line.
        requirements_txt_path_exp = os.path.join(os.getcwd(), "requirements.txt")
        parse_packages_names_mock.return_value = ["pyyaml"]
        get_packages_info_mock.return_value = {}
        check_git_only_restriction_mock.return_value = True
        get_requirements_txt_path_mock.return_value = (requirements_txt_path_exp, False)
        parse_requirements_txt_mock.return_value = {
            "appdata": "0.2.1",
            "PyYAML": "6.0",
        }

        remove_uninstalled_packages_from_requirements_txt(["pyyaml"])

        with open(requirements_txt_path_exp, "r") as f:
            assert f.read() == "appdata==0.2.1\n"
