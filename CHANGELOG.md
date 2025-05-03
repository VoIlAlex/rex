# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [2.0.13] - 2025-05-03
### Fixes
- Re-branded to `rex`.


## [2.0.7] - 2024-02-20
### Fixes
- `to-requirements.txt` isn't installed after rerunning `rt i`.
- Fix in venv folder resolution for sourcing "activate".


## [2.0.6] - 2024-02-14
### Fixes
- Remove redundant prints.


## [2.0.5] - 2024-02-14
### Fixes
- Critical bug with requirements overriding.


## [2.0.4] - 2024-02-14
### Fixed 
- Local packages and git packages installation doesn't add version to the end.
- None version isn't displayed anymore.


## [1.3.0] - 2022-07-13
### Added
- Command `alias` to enable sourced mode of cli execution. Works with `bash` and `zsh` shells.
- Entry point of cli moved to bash script.
- Sourced mode of cli execution. Allows activating virtual environment by `rt i`.
- Small refactoring.


## [1.2.0] - 2022-07-06
### Added
- Command `init` to initialize VirtualEnv-based Python project.
- Command `setup` renamed to `install`.
- Command `show` to show contents of `requirements.txt` file.
- Colored output in `init` command with `--verbose` option available.
- Alias `rt` as alternative to `requirements-txt` script.
- Alias `s` as alternative to command `show`.
- Alias `i` as alternative to command `init`.
- Docstrings to available commands.
- Project restructure and refactoring.
- Beautiful logging.

## [1.0.1 - 1.1.10] - 2021-12-31 - 2022-06-21
### Added
- Initial project setup.
- Basic configuration options.
- Command to override `pip` scripts to handle `requirements.txt` file automatically.
