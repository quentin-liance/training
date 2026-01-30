# Training Project

A Python project with development container, UV package manager, and CI/CD setup.

## Setup

### Using Dev Container (Recommended)

1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Press `Ctrl+Shift+P` and select "Dev Containers: Reopen in Container"
4. The container will build and set up automatically

### Local Setup

1. Install UV:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Create virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Linux/macOS
   # or .venv\Scripts\activate on Windows
   uv pip install -e '.[dev]'
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Project Structure

```
.
├── .devcontainer/       # Development container configuration
├── .github/            # GitHub Actions CI/CD
├── src/                # Source code
├── tests/              # Test files
├── data/               # Data files (ignored by git)
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## Development

### Running Tests

```bash
pytest
```

### Linting and Formatting

```bash
ruff check .
ruff format .
```

### Type Checking

```bash
mypy src/
```

## CI/CD

The project uses GitHub Actions for continuous integration. On each push:
- Code is linted and formatted
- Type checking is performed
- Tests are run with coverage report
