# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2025-02-04

Use dedicated dotenv file.

- Only inspect `hadalized.env` files for configuration options.
- Add `config options` subcommand to inspect configuration options.

BaseSettings appears to pass the entire contents of a dotenv file as
init args, which causes validation errors when extra init args are
forbidden.

## [0.4.0] - 2026-02-04
### Added
- Load user defined config and template files.
- Suppport dry-runs.

## [0.3.0] - 2026-01
### Added
- Introduce proper cli as main entry point via cyclopts.
- Targetted builds.
- Lazy `ColorInfo` parsing.


## [1.0.0] - 2021-07-19
### Added
- devicely.FarosReader can both read from and write to EDF files and directories
- devicely.FarosReader has as attributes the individual dataframes (ACC, ECG, ...) and not only the joined dataframe

### Changed
- in devicely.SpacelabsReader, use xml.etree from the standard library instead of third-party "xmltodict"
- switch from setuptools to Poetry

### Removed
- removed setup.py because static project files such as pyproject.toml are preferred
