# VS Code Dev Container Configuration

This devcontainer.json file configures the development environment:

## Container Setup
- **name**: Python Dev Container
- **dockerComposeFile**: Uses docker-compose.yml for container orchestration
- **service**: References the "app" service from docker-compose.yml
- **workspaceFolder**: Sets /workspace as the working directory

## VS Code Extensions
Automatically installs essential extensions:
- Python language support (Python, Pylance)
- Jupyter notebook support
- Ruff linter and formatter
- Black code formatter
- GitLens and Git Graph for enhanced Git integration

## Settings
- Python interpreter: /workspace/.venv/bin/python
- Auto-activate virtual environment in terminal
- Format on save enabled
- Auto-organize imports on save
- Ruff as default Python formatter

## Post-Create Command
After container creation:
1. Initialize git repository if not present
2. Create/clear virtual environment with UV
3. Install project dependencies
4. Install pre-commit hooks

## User
- Runs as root user for full container access
