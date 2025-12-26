# Contributing to Remote Control

We welcome contributions to the Remote Control project! This guide will help you get started.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Style](#code-style)
4. [Testing](#testing)
5. [Submitting Changes](#submitting-changes)
6. [Bug Reports](#bug-reports)
7. [Feature Requests](#feature-requests)

## Getting Started

### Prerequisites

Before contributing, make sure you have:

- **Python 3.8+** installed
- **Git** for version control
- **Development environment** set up (see [PREREQUISITES.md](PREREQUISITES.md))
- **Basic understanding** of the project structure

### Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/remote-control.git
cd remote-control

# Add upstream remote
git remote add upstream https://github.com/Nsfr750/remote-control.git
```

## Development Setup

### Environment Setup

```bash
# Create virtual environment
python -m venv venv312

# Activate (Windows)
venv312\Scripts\activate

# Activate (Linux)
source venv312/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Project Structure

Familiarize yourself with the project structure:

```
remote-control/
├── client/          # Client application
├── server/          # Server application
├── common/          # Shared code
├── setup/           # Build scripts
├── tests/           # Test suite
└── docs/            # Documentation
```

## Code Style

### Formatting Standards

We use the following tools and standards:

#### Black Formatting
```bash
# Format code
black client/ server/ common/

# Check formatting
black --check client/ server/ common/
```

#### Linting
```bash
# Run flake8
flake8 client/ server/ common/

# Run mypy for type checking
mypy client/ server/ common/
```

### Code Guidelines

#### Python Style
- Follow **PEP 8** style guide
- Use **type hints** consistently
- Keep lines under **88 characters** (Black standard)
- Use **docstrings** for all functions and classes

#### Naming Conventions
```python
# Variables and functions: snake_case
user_name = "admin"
def connect_to_server():
    pass

# Classes: PascalCase
class RemoteControlClient:
    pass

# Constants: UPPER_CASE
MAX_CONNECTIONS = 100
DEFAULT_PORT = 5000
```

#### Import Organization
```python
# Standard library imports first
import os
import sys
import logging

# Third-party imports next
from PyQt6.QtWidgets import QMainWindow
import numpy as np

# Local imports last
from common.protocol import MessageType
from client.gui import MainWindow
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_client.py

# Run with coverage
pytest --cov=client --cov=server --cov=common
```

### Writing Tests

#### Test Structure
```python
import pytest
from unittest.mock import Mock, patch

class TestRemoteControlClient:
    def test_init(self):
        """Test client initialization."""
        client = RemoteControlClient()
        assert client is not None
    
    def test_connect_to_server_success(self):
        """Test successful server connection."""
        client = RemoteControlClient()
        with patch('socket.socket') as mock_socket:
            result = client.connect_to_server("localhost", 5000, "user", "pass")
            assert result is True
```

#### Test Coverage
- Aim for **80%+ code coverage**
- Test both **success and failure** cases
- Use **mocks** for external dependencies
- Test **edge cases** and error conditions

### Test Categories

- **Unit Tests**: Individual functions and methods
- **Integration Tests**: Component interactions
- **End-to-End Tests**: Complete user workflows
- **Platform Tests**: Windows and Linux specific functionality

## Submitting Changes

### Branch Strategy

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Create bugfix branch
git checkout -b fix/issue-number-description
```

### Commit Guidelines

#### Commit Messages
Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation change
- `style`: Code style change
- `refactor`: Code refactoring
- `test`: Add or modify tests
- `chore`: Maintenance task

Examples:
```
feat(client): add fullscreen exit with ESC key

Fix mouse click handling on Linux servers

docs(api): update file transfer documentation

style(server): apply black formatting
```

### Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Add entries to CHANGELOG.md
   - Update API.md for API changes

2. **Run Tests**
   ```bash
   # Ensure all tests pass
   pytest
   
   # Check code style
   black --check .
   flake8 .
   ```

3. **Create Pull Request**
   - Push to your fork
   - Create PR against `main` branch
   - Fill out PR template completely
   - Link relevant issues

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## Bug Reports

### Reporting Bugs

Use the following template for bug reports:

```markdown
**Bug Description**
Clear and concise description of the bug.

**Steps to Reproduce**
1. Go to...
2. Click on...
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 11, Ubuntu 22.04]
- Python Version: [e.g., 3.9.7]
- Application Version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information, logs, or screenshots.
```

### Debug Information

Enable debug logging to provide useful information:

```bash
# Client debug
python -m client.client --host localhost --port 5000 --debug

# Server debug
python -m server.server --host 0.0.0.0 --port 5000 --debug
```

## Feature Requests

### Requesting Features

Use this template for feature requests:

```markdown
**Feature Description**
Clear description of the feature you want.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
How do you envision this feature working?

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Any other relevant information or use cases.
```

## Development Guidelines

### Security Considerations

- **Never commit** sensitive information (passwords, API keys)
- **Validate all input** from external sources
- **Use secure defaults** for configuration
- **Follow OWASP guidelines** for security

### Performance Considerations

- **Profile code** before optimizing
- **Consider memory usage** for long-running processes
- **Optimize network calls** for latency
- **Use efficient algorithms** for data processing

### Platform Considerations

- **Test on both Windows and Linux**
- **Handle platform-specific differences** gracefully
- **Document platform requirements** clearly
- **Use abstraction layers** for platform code

## Review Process

### Code Review Criteria

- **Functionality**: Does the code work as intended?
- **Style**: Does it follow project guidelines?
- **Tests**: Are tests comprehensive and passing?
- **Documentation**: Is the code well documented?
- **Security**: Are security implications considered?

### Review Guidelines

- **Be constructive** and respectful
- **Focus on the code**, not the author
- **Explain reasoning** for suggested changes
- **Ask questions** if something is unclear

## Community Guidelines

### Communication

- **Use GitHub issues** for bug reports and feature requests
- **Join discussions** for general questions
- **Be patient** with response times
- **Follow the code of conduct** (see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md))

### Recognition

Contributors are recognized in:
- **README.md** contributors section
- **CHANGELOG.md** for significant contributions
- **Release notes** for new features
- **GitHub contributor statistics**

## Getting Help

### Resources

- **Documentation**: [docs/](./) directory
- **API Reference**: [API.md](API.md)
- **Architecture**: [STRUCTURE.md](STRUCTURE.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Contact

- **Issues**: [GitHub Issues](https://github.com/Nsfr750/remote-control/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Nsfr750/remote-control/discussions)
- **Security**: [info@tuxxle.org](mailto:info@tuxxle.org)

---

Thank you for contributing to Remote Control! Your contributions help make this project better for everyone.

**Last Updated**: December 26, 2025  
**Version**: 1.0.0
