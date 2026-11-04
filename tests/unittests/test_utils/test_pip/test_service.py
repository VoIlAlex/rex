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

        parse_packages_names_mock.assert_called_once_with(
            ["something"], command="uninstall"
        )
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

        parse_packages_names_mock.assert_called_once_with(
            ["something"], command="uninstall"
        )
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

        parse_packages_names_mock.assert_called_once_with(
            ["something"], command="uninstall"
        )
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


@patch("requirements_txt.utils.pip.service.get_packages_info")
@patch("requirements_txt.utils.pip.service.check_git_only_restriction")
class TestRequirementsTxtRoundTrip:
    def _install(self, args, installed, get_packages_info_mock, git_mock, content):
        git_mock.return_value = True
        get_packages_info_mock.return_value = installed
        with open("requirements.txt", "w") as f:
            f.write(content)
        add_installed_packages_to_requirements_txt(args)
        with open("requirements.txt") as f:
            return f.read()

    def test_unpinned_lines_are_not_corrupted(
        self, git_mock: Mock, get_packages_info_mock: Mock, temp_dir
    ):
        # Previously rewritten as `flask==None` and `foo>=1.0==None`.
        result = self._install(
            ["appdata"],
            {"appdata": "2.2.1"},
            get_packages_info_mock,
            git_mock,
            "flask\nfoo>=1.0\n",
        )
        assert result == "flask\nfoo>=1.0\nappdata==2.2.1\n"

    def test_extras_are_written(
        self, git_mock: Mock, get_packages_info_mock: Mock, temp_dir
    ):
        result = self._install(
            ["requests[socks]>=2"],
            {"requests": "2.31.0"},
            get_packages_info_mock,
            git_mock,
            "",
        )
        get_packages_info_mock.assert_called_once_with(["requests"])
        assert result == "requests[socks]==2.31.0\n"

    def test_existing_line_for_same_project_is_replaced_in_place(
        self, git_mock: Mock, get_packages_info_mock: Mock, temp_dir
    ):
        result = self._install(
            ["requests"],
            {"requests": "2.31.0"},
            get_packages_info_mock,
            git_mock,
            "appdata==2.2.1\nRequests>=2.0\nclick==8.0.3\n",
        )
        assert result == "appdata==2.2.1\nrequests==2.31.0\nclick==8.0.3\n"

    def test_option_values_are_not_written(
        self, git_mock: Mock, get_packages_info_mock: Mock, temp_dir
    ):
        result = self._install(
            ["-i", "https://example.org/simple", "appdata"],
            {"appdata": "2.2.1"},
            get_packages_info_mock,
            git_mock,
            "",
        )
        get_packages_info_mock.assert_called_once_with(["appdata"])
        assert result == "appdata==2.2.1\n"


@patch("requirements_txt.utils.pip.service.get_packages_info")
@patch("requirements_txt.utils.pip.service.check_git_only_restriction")
class TestRequirementsTxtEncoding:
    def test_utf_16_crlf_file_is_updated_in_place(
        self, git_mock: Mock, get_packages_info_mock: Mock, temp_dir
    ):
        # `pip freeze > requirements.txt` in Windows PowerShell (#32).
        git_mock.return_value = True
        get_packages_info_mock.return_value = {"appdata": "2.2.1"}
        with open("requirements.txt", "wb") as f:
            f.write("click==8.0.3\r\n".encode("utf-16"))

        add_installed_packages_to_requirements_txt(["appdata"])

        with open("requirements.txt", "rb") as f:
            data = f.read()
        assert data.decode("utf-16") == "click==8.0.3\r\nappdata==2.2.1\r\n"
