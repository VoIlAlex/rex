import os.path

from requirements_txt.utils.files import read_text_file


def show_requirements_txt():
    requirement_text_path = os.path.join(os.getcwd(), "requirements.txt")
    requirements_txt_content = read_text_file(requirement_text_path).text
    print(requirements_txt_content)


__all__ = [
    "show_requirements_txt",
]
