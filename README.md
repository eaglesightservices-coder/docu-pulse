# docu-pulse

[![Build Status](https://github.com/eaglesightservices-coder/docu-pulse/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/eaglesightservices-coder/docu-pulse/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/Code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI](https://img.shields.io/pypi/v/docu-pulse.svg)](https://pypi.org/project/docu-pulse/)

**docu-pulse** is a lightweight, modular CLI utility that analyzes Python repositories for code quality, docstring completeness, and API documentation gaps. It generates automated health reports to help you maintain comprehensive documentation standards across your codebase.

## Features

✨ **Core Capabilities**
- **Docstring Analysis**: Scan Python files for missing function, method, and class docstrings
- **Coverage Metrics**: Calculate documentation coverage percentages at file and project level
- **Multi-Format Reports**: Generate reports in JSON and interactive HTML formats
- **Flexible Configuration**: Customize analysis with options to include/exclude private members and test files
- **Cross-Platform**: Runs on Linux, macOS, and Windows
- **Zero Dependencies**: Uses only Python standard library for core functionality

🎯 **Quality Features**
- AST-based parsing for accurate docstring detection
- Syntax error handling with detailed error reporting
- Configurable coverage thresholds with CI/CD integration
- Private method/function filtering
- Test file exclusion (configurable)
- Batch file processing with progress tracking

## Installation

### Via pip (Recommended)

```bash
pip install docu-pulse
```

### From Source

```bash
git clone https://github.com/eaglesightservices-coder/docu-pulse.git
cd docu-pulse
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/eaglesightservices-coder/docu-pulse.git
cd docu-pulse
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

Analyze the current directory:
```bash
docu-pulse
```

Analyze a specific directory:
```bash
docu-pulse /path/to/project
```

Analyze a single file:
```bash
docu-pulse myfile.py
```

### Generate Reports

Generate a JSON report:
```bash
docu-pulse . --output report.json
```

Generate an interactive HTML report:
```bash
docu-pulse . --html report.html
```

### Advanced Options

Include private methods in analysis:
```bash
docu-pulse . --include-private
```

Include test files:
```bash
docu-pulse . --include-tests
```

Set minimum coverage threshold (fails if below):
```bash
docu-pulse . --min-coverage 80
```

Combine options:
```bash
docu-pulse . --include-private --html report.html --min-coverage 75
```

Verbose output with detailed file information:
```bash
docu-pulse . --verbose
```

## Usage Examples

### Example 1: Analyze Current Project

```bash
$ docu-pulse .
======================================================================
📊  docu-pulse - Documentation Health Report
======================================================================

📁 Files Analyzed:        5
📝 Total Items:           23
✅ Documented Items:      18
📈 Overall Coverage:      78.26%
⚠️  Files with Errors:     0

======================================================================
```

### Example 2: Generate HTML Report for CI/CD

```bash
$ docu-pulse src/ --html coverage-report.html --min-coverage 80
✅ HTML report saved to: coverage-report.html

$ echo "Report generated successfully"
```

### Example 3: Detailed Analysis with Verbose Output

```bash
$ docu-pulse . --verbose --output metrics.json
======================================================================
📊  docu-pulse - Documentation Health Report
======================================================================

📁 Files Analyzed:        3
📝 Total Items:           12
✅ Documented Items:      10
📈 Overall Coverage:      83.33%
⚠️  Files with Errors:     0

----------------------------------------------------------------------
Detailed File Analysis:
----------------------------------------------------------------------

📄 docupulse/core.py
   Coverage: 95.00% (19/20)
   Missing docstrings:
      • _extract_items (function) at line 145

📄 docupulse/cli.py
   Coverage: 90.00% (9/10)
   Missing docstrings:
      • format_summary (function) at line 42

📄 docupulse/__init__.py
   Coverage: 100.00% (2/2)

======================================================================
✅ JSON report saved to: metrics.json
```

### Example 4: CI/CD Integration

Add to your GitHub Actions workflow:
```yaml
- name: Check Documentation Coverage
  run: |
    docu-pulse . --min-coverage 80 --html docs-report.html
```

Or fail if coverage drops below threshold:
```bash
docu-pulse . --min-coverage 85 || exit 1
```

## Command-Line Reference

```
usage: docu-pulse [-h] [--version] [-o FILE] [--html FILE] 
                  [--include-private] [--include-tests] 
                  [--min-coverage PERCENT] [-q] [-v]
                  [path]

positional arguments:
  path                  Path to analyze (default: current directory)

optional arguments:
  -h, --help            Show this help message and exit
  --version             Show version number and exit
  -o, --output FILE     Save JSON report to file
  --html FILE           Export HTML report to file
  --include-private     Include private methods/functions in analysis
  --include-tests       Include test files in analysis
  --min-coverage PERCENT
                        Exit with error if coverage is below percentage
  -q, --quiet           Suppress standard output
  -v, --verbose         Print detailed analysis per file
```

## API Usage

Use docu-pulse programmatically in your Python code:

```python
from docupulse import DocumentationAnalyzer

# Create analyzer
analyzer = DocumentationAnalyzer(
    ignore_private=True,
    ignore_tests=True
)

# Analyze directory
report = analyzer.analyze_directory('./src')

# Generate reports
analyzer.export_json(report, 'report.json')
analyzer.export_html(report, 'report.html')

# Access summary data
summary = report['summary']
print(f"Coverage: {summary['overall_coverage']}%")
```

## Report Format

### JSON Report Structure

```json
{
  "summary": {
    "files_analyzed": 5,
    "total_items": 23,
    "documented_items": 18,
    "overall_coverage": 78.26,
    "files_with_errors": 0
  },
  "files": [
    {
      "file_path": "docupulse/core.py",
      "total_items": 10,
      "documented_items": 9,
      "coverage_percentage": 90.0,
      "missing_docstrings": [
        {
          "name": "some_function",
          "type": "function",
          "line": 42
        }
      ],
      "errors": []
    }
  ]
}
```

### HTML Report

Interactive HTML reports include:
- Summary statistics with visual cards
- File-by-file coverage breakdown
- Progress bars showing coverage percentages
- Missing docstring details with line numbers
- Error reporting for files with syntax issues

## Configuration

### Environment Variables

Currently, docu-pulse doesn't use environment variables, but this is planned for future versions.

### Configuration File

Configuration via files is planned for v0.2.0. Currently use command-line options.

## Roadmap

### Version 0.1.0 (Current)
- [x] Core AST-based docstring scanning
- [x] CLI with argparse
- [x] JSON and HTML report generation
- [x] Test suite with pytest
- [x] GitHub Actions CI/CD
- [x] PyPI packaging

### Version 0.2.0 (Planned)
- [ ] Configuration file support (.docu-pulse.yaml)
- [ ] Integration with pre-commit hooks
- [ ] Additional report formats (CSV, XML)
- [ ] Docstring quality validation (check for empty docstrings)
- [ ] Custom plugin system for analysis rules

### Version 0.3.0 (Planned)
- [ ] **AI-Powered Remediation**: Automated docstring generation suggestions
- [ ] **OpenAI Codex Integration**: Leverage Codex for smart documentation suggestions
- [ ] Interactive CLI mode for real-time feedback
- [ ] Performance optimizations for large codebases
- [ ] Web dashboard for monitoring trends

### Future Roadmap
- [ ] Language support beyond Python (JavaScript, Go, Rust)
- [ ] IDE integrations (VSCode, PyCharm extensions)
- [ ] Team collaboration features
- [ ] Historical tracking and trend analysis
- [ ] Slack/Teams integration for automated reporting

## Development

### Setting Up Development Environment

```bash
git clone https://github.com/eaglesightservices-coder/docu-pulse.git
cd docu-pulse
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest tests/ -v --cov=docupulse
```

### Code Quality Checks

```bash
black docupulse tests
isort docupulse tests
flake8 docupulse tests
mypy docupulse
```

### Building Distribution

```bash
pip install build
python -m build
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup instructions
- Code style guidelines
- Testing requirements
- Pull request process
- Issue reporting guidelines

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use docu-pulse in your research or project, please cite it as:

```bibtex
@software{docu_pulse_2024,
  title={docu-pulse: Documentation Health Analysis for Python},
  author={docu-pulse Contributors},
  year={2024},
  url={https://github.com/eaglesightservices-coder/docu-pulse}
}
```

## Support

- 📖 **Documentation**: [README](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/eaglesightservices-coder/docu-pulse/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/eaglesightservices-coder/docu-pulse/discussions)
- 📧 **Email**: contributors@docu-pulse.dev

## Acknowledgments

- Built with ❤️ for the Python community
- Inspired by tools like coverage.py, flake8, and black
- Thanks to all contributors and users providing feedback

## Related Projects

- [coverage.py](https://coverage.readthedocs.io/) - Code coverage measurement
- [flake8](https://flake8.pycqa.org/) - Python linting
- [black](https://black.readthedocs.io/) - Code formatter
- [pylint](https://pylint.pycqa.org/) - Code analysis

---

**Give us a ⭐ on GitHub if you find docu-pulse useful!**
This is just the beginning of a new horizon for the developer community!
This project represents the beginning of an ambitious roadmap. There will be accelerated development from early release to a full-featured v1.0 release with zero paywalls. Our goal is to make automated codebase quality accessible to all open-source developers, and to provide the velocity needed to build an active, thriving community.

[GitHub Repository](https://github.com/eaglesightservices-coder/docu-pulse) • [PyPI Package](https://pypi.org/project/docu-pulse/) • [Issue Tracker](https://github.com/eaglesightservices-coder/docu-pulse/issues)
