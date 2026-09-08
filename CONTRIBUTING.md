# Contributing to docu-pulse

Thank you for your interest in contributing to **docu-pulse**! We welcome contributions from everyone, whether it's bug reports, feature requests, documentation improvements, or code contributions.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. We are committed to providing a welcoming and inclusive environment for all contributors.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip package manager

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/eaglesightservices-coder/docu-pulse.git
   cd docu-pulse
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Creating a Branch

Create a descriptive branch for your changes:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

Use prefixes like:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation improvements
- `refactor/` for code refactoring
- `test/` for test additions

### Making Changes

1. **Write clean, well-documented code** following PEP 8 standards
2. **Add tests** for any new functionality
3. **Update documentation** if needed
4. **Run linting and formatting**:
   ```bash
   black docupulse tests
   isort docupulse tests
   flake8 docupulse tests
   mypy docupulse
   ```

5. **Run tests** to ensure everything passes:
   ```bash
   pytest tests/ -v --cov=docupulse
   ```

### Commit Messages

Write clear, descriptive commit messages:
```
Short description (50 chars or less)

Detailed explanation of the changes (if needed). Wrap at 72 characters.
Can include multiple paragraphs.

Fixes #123 (if applicable)
```

### Pushing Changes

Push your branch to your fork:
```bash
git push origin feature/your-feature-name
```

### Creating a Pull Request

1. Go to the repository on GitHub
2. Click "New Pull Request"
3. Select your branch and provide a clear description
4. Link any related issues using `Fixes #123` syntax
5. Wait for CI checks to pass and for code review

## Pull Request Guidelines

- Keep PRs focused on a single concern
- Provide a clear description of changes
- Include tests for new functionality
- Ensure all CI checks pass
- Respond to reviewer feedback promptly

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=docupulse --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run specific test
pytest tests/test_core.py::TestDocumentationAnalyzer::test_analyze_file_with_docstrings
```

### Writing Tests

- Use descriptive test names that explain what is being tested
- Group related tests in classes
- Use fixtures for common setup
- Aim for high coverage (>80%)

Example:
```python
def test_analyze_file_with_docstrings():
    """Test analyzing a file with properly documented functions."""
    code = '''
def documented_function():
    """This function is documented."""
    pass
'''
    # Test implementation
```

## Code Style

We follow PEP 8 and use:
- **black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

### Format Your Code

Before committing, format your code:
```bash
black docupulse tests
isort docupulse tests
```

## Documentation

- Update `README.md` for user-facing changes
- Add docstrings to all public functions and classes
- Use Google-style docstrings:
  ```python
  def analyze_file(self, file_path: str) -> AnalysisResult:
      """
      Analyze a single Python file.

      Args:
          file_path: Path to the Python file to analyze.

      Returns:
          AnalysisResult object containing the analysis data.
      """
  ```

## Reporting Issues

### Bug Reports

Include:
- Python version
- Operating system
- Exact command that reproduces the issue
- Expected behavior vs actual behavior
- Error messages and tracebacks

### Feature Requests

Include:
- Use case and motivation
- Example usage
- Potential implementation approach (if known)

## Release Process

Maintainers handle releases. Version numbers follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

## Additional Resources

- **GitHub Issues**: [Report bugs or request features](https://github.com/eaglesightservices-coder/docu-pulse/issues)
- **Discussions**: [Ask questions or discuss ideas](https://github.com/eaglesightservices-coder/docu-pulse/discussions)
- **Documentation**: [Read the README and docs](https://github.com/eaglesightservices-coder/docu-pulse#readme)

## Questions?

Feel free to:
- Open a GitHub discussion
- Ask in pull request comments
- Check existing issues and documentation

## Thank You!

Your contributions make docu-pulse better for everyone. We appreciate your time and effort in helping us improve this project!

---

**Happy coding!** 🚀
