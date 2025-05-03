from distutils.core import setup
import os
from setuptools import find_packages
from requirements_txt import __version__

# User-friendly description from README.md
current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    with open(os.path.join(current_directory, "README.md"), encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = ""


def run_setup(package_name: str, directory: str = "."):
    setup(
        # Name of the package
        name=package_name,
        # Packages to include into the distribution
        packages=find_packages(directory),
        # Start with a small number and increase it with
        # every change you make https://semver.org
        version=__version__,
        # Chose a license from here: https: //
        # help.github.com / articles / licensing - a -
        # repository. For example: MIT
        license="MIT",
        # Short description of your library
        description="Automatically add and delete modules to requirements.txt installing them using pip.",
        # Long description of your library
        long_description=long_description,
        long_description_content_type="text/markdown",
        # Your name
        author="Ilya Vouk",
        # Your email
        author_email="ilya.vouk@gmail.com",
        # Either the link to your github or to your website
        url="https://github.com/VoIlAlex/rex",
        # Link from which the project can be downloaded
        download_url="https://github.com/VoIlAlex/rex/archive/refs/tags/v2.0.14.zip",
        # List of keywords
        keywords=[
            "pip",
            "requirements.txt",
            "dependency",
            "dependencies",
            "requirements",
            "packages",
            "wrapper",
            "repository",
        ],
        # List of packages to install with this one
        install_requires=[
            "appdata==2.2.1",
            "click>=8.0.3",
            "colored>=1.4.3",
        ],
        entry_points={
            "console_scripts": [
                "requirements-txt-cli = requirements_txt.commands:cli",
                "rt-cli = requirements_txt.commands:cli",
                "rex-cli = requirements_txt.commands:cli",
            ],
        },
        scripts=["scripts/rt", "scripts/requirements-txt", "scripts/rex"],
        # https://pypi.org/classifiers/
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: Unix",
            "Topic :: Software Development",
            "Topic :: System :: Installation/Setup",
            "Topic :: Terminals",
            "Topic :: Utilities",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
        ],
    )
