# Dependencies Management

This document explains how dependencies are managed in the Indic Seamless Service project.

## Overview

- **`env/requirements.in`** - Direct dependencies (unlocked versions)
- **`env/requirements.txt`** - Locked dependencies (all dependencies with exact versions)

## Quick Start

```bash
# Install dependencies
pip install -r env/requirements.txt
```

## Adding Dependencies

1. Add the dependency to `env/requirements.in`:
   ```bash
   echo "new-package" >> env/requirements.in
   ```

2. Compile the requirements:
   ```bash
   pip-compile env/requirements.in --upgrade
   ```

3. Install the updated requirements:
   ```bash
   pip install -r env/requirements.txt
   ```

## Updating Dependencies

```bash
# Update all dependencies to latest compatible versions
pip-compile env/requirements.in --upgrade

# Update specific dependency
pip-compile env/requirements.in --upgrade-package package-name

# Install updated requirements
pip install -r env/requirements.txt
```

## Environment Management

```bash
# Sync virtual environment with requirements
pip-sync env/requirements.txt
```

## Development Workflow

```bash
# Install all dependencies
pip install -r env/requirements.txt
```

## Project Structure

```
indic_seamless_service/
├── env/
│   ├── requirements.in          # Direct dependencies
│   ├── requirements.txt         # Locked dependencies (auto-generated)
│   └── setup.sh                # Automated setup script
└── .gitignore              # Excludes venv and cache files
```

## Commands Reference

```bash
# Compile requirements
pip-compile env/requirements.in

# Install dependencies
pip install -r env/requirements.txt

# Sync environment
pip-sync env/requirements.txt

# Show dependency tree
pip list
```

## Troubleshooting

1. **Version Conflicts**: Run `pip-compile --upgrade` to resolve
2. **Missing Dependencies**: Check if they're in the correct `.in` file
3. **Virtual Environment Issues**: Delete `venv/` and recreate with `./env/setup.sh`

### Commands Reference

- `pip-compile env/requirements.in` - Generate requirements.txt
- `pip install -r env/requirements.txt` - Install dependencies
- `pip-sync env/requirements.txt` - Sync environment exactly
- `pip list` - Show installed packages 