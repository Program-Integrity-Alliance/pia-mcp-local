# Contributing to PIA MCP Server

Thank you for your interest in contributing to the PIA MCP Server! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Pre-commit Hooks](#pre-commit-hooks)
- [Making Changes](#making-changes)
- [Commit Guidelines](#commit-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Code Style](#code-style)

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please treat all community members with respect and create a welcoming environment for everyone.

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- A GitHub account

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/pia-mcp-local.git
   cd pia-mcp-local
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/Program-Integrity-Alliance/pia-mcp-local.git
   ```

## 💻 Development Setup

1. **Create and activate virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   uv pip install -e ".[test,dev]"
   ```

3. **Verify installation:**
   ```bash
   python -m pytest
   ```

## 🔧 Pre-commit Hooks

We use pre-commit hooks to ensure code quality and consistency. **This is required for all contributors.**

### Install Pre-commit

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the git hook scripts
pre-commit install
```

### What Pre-commit Does

Our pre-commit configuration (`.pre-commit-config.yaml`) automatically:

- **Code Formatting**: Runs `black` to format Python code
- **File Checks**: Removes trailing whitespace, fixes end-of-file formatting
- **YAML/JSON Validation**: Checks syntax of configuration files
- **Merge Conflict Detection**: Prevents committing unresolved conflicts
- **Large File Prevention**: Blocks accidentally committed large files

### Running Pre-commit Manually

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Skip pre-commit for emergency commits (not recommended)
git commit --no-verify -m "emergency fix"
```

### Pre-commit Configuration

Our `.pre-commit-config.yaml` includes:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.11
```

## 🛠️ Making Changes

### Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make your changes:**
   - Write code following our [Code Style](#code-style)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   # Run tests
   python -m pytest

   # Run with coverage
   python -m pytest --cov=pia_mcp_server

   # Run pre-commit checks
   pre-commit run --all-files
   ```

4. **Commit your changes** (see [Commit Guidelines](#commit-guidelines))

5. **Push and create PR:**
   ```bash
   git push origin feat/your-feature-name
   ```

### Types of Contributions

- **Bug Fixes**: Fix existing issues
- **Features**: Add new functionality
- **Documentation**: Improve docs, examples, or comments
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **Refactoring**: Improve code structure without changing functionality

## 📝 Commit Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

### Commit Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Commit Types

- **feat:** New features
- **fix:** Bug fixes
- **docs:** Documentation changes
- **style:** Code style changes (formatting, etc.)
- **refactor:** Code refactoring
- **test:** Adding or modifying tests
- **chore:** Build process or auxiliary tool changes
- **perf:** Performance improvements
- **ci:** CI/CD pipeline changes
- **build:** Build system or dependencies

### Examples

```bash
feat: add new OData string function support
fix: resolve API key validation error
docs: update README with filter examples
test: add unit tests for pia_search_content tool
chore: update dependencies to latest versions
```

### Commit Best Practices

- Keep commits atomic (one logical change per commit)
- Write clear, descriptive commit messages
- Reference issues when applicable: `fixes #123`
- Use imperative mood: "add feature" not "added feature"

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=pia_mcp_server --cov-report=html

# Run specific test file
python -m pytest tests/test_tools.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_pia_search_content_with_valid_filters`
- Mock external API calls
- Test both success and error scenarios
- Aim for high test coverage (>90%)

### Test Structure

```python
import pytest
from unittest.mock import patch, AsyncMock

async def test_tool_functionality():
    """Test description explaining what this tests."""
    # Arrange
    test_data = {"query": "test"}

    # Act
    result = await handle_tool(test_data)

    # Assert
    assert len(result) == 1
    assert "expected content" in result[0].text
```

## 🔍 Pull Request Process

### Before Submitting

1. **Update your branch:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks:**
   ```bash
   python -m pytest
   pre-commit run --all-files
   ```

3. **Update documentation** if needed

### PR Guidelines

- **Title**: Use conventional commit format
- **Description**: Clearly explain what and why
- **Link Issues**: Reference related issues
- **Screenshots**: Include for UI changes
- **Breaking Changes**: Clearly document any breaking changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other: ___

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Peer Review**: At least one maintainer reviews the code
3. **Feedback**: Address any requested changes
4. **Approval**: Maintainer approves and merges

## 🐛 Issue Guidelines

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check documentation** for common solutions
3. **Test with latest version**

### Bug Reports

Include:
- **Environment**: OS, Python version, package version
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Error messages** (full stack trace)
- **Minimal code example**

### Feature Requests

Include:
- **Clear description** of the feature
- **Use case** and motivation
- **Proposed solution** (if you have one)
- **Alternatives considered**

## 🎨 Code Style

### Python Style Guide

- **Formatter**: Black (configured in `pyproject.toml`)
- **Line Length**: 88 characters (Black default)
- **Import Sorting**: isort (if configured)
- **Type Hints**: Use type hints for function signatures
- **Docstrings**: Google style docstrings

### Code Quality

- **Functions**: Keep functions small and focused
- **Names**: Use descriptive variable and function names
- **Comments**: Explain why, not what
- **Error Handling**: Use appropriate exception handling
- **Logging**: Use structured logging with appropriate levels

### Example

```python
"""Module for handling PIA search operations."""

import logging
from typing import Dict, Any, List
import mcp.types as types

logger = logging.getLogger(__name__)


async def handle_pia_search_content(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle PIA search requests with OData filtering.

    Args:
        arguments: Search parameters including query and filters

    Returns:
        List of text content with search results

    Raises:
        ValueError: If required parameters are missing
    """
    try:
        # Implementation here
        pass
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise
```

## 🚀 Release Process

For maintainers:

1. **Version Bump**: Update version in `pyproject.toml`
2. **Changelog**: Update CHANGELOG.md
3. **Tag Release**: Create git tag
4. **GitHub Release**: Create release with notes
5. **PyPI**: Automated via GitHub Actions

## 📞 Getting Help

- **Documentation**: Check the README and code comments
- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for sensitive issues

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- CONTRIBUTORS.md file (if created)

Thank you for contributing to the PIA MCP Server! 🎉
