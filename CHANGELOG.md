# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- MIT License
- Comprehensive logging system throughout the application
- Logger in `calculations.py` with INFO and DEBUG levels
- Logger in `app.py` with file and console handlers
- CHANGELOG.md following Keep a Changelog format

### Changed
- Replaced deprecated `use_container_width=True` with `width='stretch'` in all Streamlit components
- Updated Streamlit config to disable CORS/XSRF warnings and usage stats

## [0.1.0] - 2026-01-31

### Added
- Type annotations for all functions in `calculations.py`
- Input validation for all calculation functions
- Protection against division by zero in `calculate_margins()`
- Handling of empty DataFrames and NaN values
- 14 new unit tests (total: 17 tests)
- Test suite for `generator.py` with 100% coverage
- Tests for edge cases: empty data, missing columns, misaligned months
- Mypy configuration with namespace packages support
- GitHub Actions CI/CD pipeline with Python 3.11 and 3.12

### Changed
- Improved docstrings with Args, Returns, and Raises sections
- Fixed imports to use absolute paths with `src.` prefix
- Updated pre-commit hooks configuration
- Coverage improved to 92% for `calculations.py` and 100% for `generator.py`

### Fixed
- Division by zero error in margin percentage calculation
- NaN values in merged DataFrames now filled with 0
- Import issues resolved with proper package structure

## [0.0.1] - 2026-01-31

### Added
- Initial Streamlit application for company margin analysis
- Fake data generator with 12 months of income and cost data
- Calculation utilities for totals and margins
- Interactive dashboard with KPIs, charts, and data tables
- Filters for months and income categories
- Export functionality for CSV downloads
- Pre-commit hooks (Ruff, mypy, nbstripout)
- Comprehensive test suite with pytest
- Code coverage reporting with pytest-cov
- README with installation and usage instructions
- `.gitignore` for Python projects
- `pyproject.toml` with all dependencies and tool configurations

[Unreleased]: https://github.com/quentin-liance/training/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/quentin-liance/training/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/quentin-liance/training/releases/tag/v0.0.1
