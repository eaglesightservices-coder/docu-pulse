"""
Core scanning logic for docupulse.

This module provides the DocumentationAnalyzer class which parses Python files,
scans for missing docstrings, calculates coverage percentages, and generates
comprehensive documentation health reports.
"""

import os
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class AnalysisResult:
    """Represents the analysis results for a single Python file."""

    file_path: str
    total_items: int
    documented_items: int
    coverage_percentage: float
    missing_docstrings: List[Dict[str, str]]
    errors: List[str]

    def to_dict(self):
        """Convert result to dictionary."""
        return asdict(self)


class DocumentationAnalyzer:
    """
    Analyzes Python repositories for documentation completeness.

    Scans Python files for missing function, method, and class docstrings,
    calculates coverage percentages, and generates health reports.
    """

    def __init__(self, ignore_private: bool = True, ignore_tests: bool = True):
        """
        Initialize the DocumentationAnalyzer.

        Args:
            ignore_private: If True, ignore private methods/functions (starting with _).
            ignore_tests: If True, ignore files in test directories.
        """
        self.ignore_private = ignore_private
        self.ignore_tests = ignore_tests
        self.results: List[AnalysisResult] = []

    def analyze_directory(self, directory: str) -> Dict:
        """
        Analyze all Python files in a directory recursively.

        Args:
            directory: Path to the directory to analyze.

        Returns:
            Dictionary containing summary statistics and detailed results.
        """
        self.results = []
        directory_path = Path(directory)

        if not directory_path.exists():
            return self._empty_report("Directory does not exist")

        python_files = list(directory_path.rglob("*.py"))

        if not python_files:
            return self._empty_report("No Python files found")

        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue

            result = self._analyze_file(str(file_path))
            if result:
                self.results.append(result)

        return self._generate_report()

    def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        Analyze a single Python file.

        Args:
            file_path: Path to the Python file to analyze.

        Returns:
            AnalysisResult object containing the analysis data.
        """
        return self._analyze_file(file_path)

    def _analyze_file(self, file_path: str) -> Optional[AnalysisResult]:
        """
        Internal method to analyze a single file.

        Args:
            file_path: Path to the Python file.

        Returns:
            AnalysisResult or None if file cannot be parsed.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (IOError, UnicodeDecodeError) as e:
            return AnalysisResult(
                file_path=file_path,
                total_items=0,
                documented_items=0,
                coverage_percentage=0.0,
                missing_docstrings=[],
                errors=[str(e)],
            )

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return AnalysisResult(
                file_path=file_path,
                total_items=0,
                documented_items=0,
                coverage_percentage=0.0,
                missing_docstrings=[],
                errors=[f"Syntax error: {str(e)}"],
            )

        items_to_check = self._extract_items(tree)
        missing = []
        documented_count = 0

        for item_name, item_type, node in items_to_check:
            has_docstring = ast.get_docstring(node) is not None
            if has_docstring:
                documented_count += 1
            else:
                missing.append(
                    {
                        "name": item_name,
                        "type": item_type,
                        "line": node.lineno,
                    }
                )

        total_items = len(items_to_check)
        coverage = (documented_count / total_items * 100) if total_items > 0 else 0.0

        return AnalysisResult(
            file_path=file_path,
            total_items=total_items,
            documented_items=documented_count,
            coverage_percentage=round(coverage, 2),
            missing_docstrings=missing,
            errors=[],
        )

    def _extract_items(self, tree: ast.AST) -> List[Tuple[str, str, ast.AST]]:
        """
        Extract all documentable items (functions, classes, methods) from AST.

        Args:
            tree: The AST tree to extract items from.

        Returns:
            List of tuples (name, type, node).
        """
        items = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if self.ignore_private and node.name.startswith("_"):
                    continue
                items.append((node.name, "function", node))
            elif isinstance(node, ast.AsyncFunctionDef):
                if self.ignore_private and node.name.startswith("_"):
                    continue
                items.append((node.name, "async_function", node))
            elif isinstance(node, ast.ClassDef):
                if self.ignore_private and node.name.startswith("_"):
                    continue
                items.append((node.name, "class", node))

        return items

    def _should_skip_file(self, file_path: Path) -> bool:
        """
        Determine if a file should be skipped during analysis.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the file should be skipped, False otherwise.
        """
        if self.ignore_tests:
            parts = file_path.parts
            if "test" in parts or "tests" in parts:
                return True
            if file_path.name.startswith("test_"):
                return True
            if file_path.name.endswith("_test.py"):
                return True

        if file_path.name.startswith("__") and file_path.name.endswith("__"):
            return True

        return False

    def _generate_report(self) -> Dict:
        """
        Generate a comprehensive report from analysis results.

        Returns:
            Dictionary containing summary statistics and detailed results.
        """
        if not self.results:
            return {
                "summary": {
                    "files_analyzed": 0,
                    "total_items": 0,
                    "documented_items": 0,
                    "overall_coverage": 0.0,
                    "files_with_errors": 0,
                },
                "files": [],
            }

        total_items = sum(r.total_items for r in self.results)
        documented_items = sum(r.documented_items for r in self.results)
        overall_coverage = (
            (documented_items / total_items * 100) if total_items > 0 else 0.0
        )
        files_with_errors = sum(1 for r in self.results if r.errors)

        return {
            "summary": {
                "files_analyzed": len(self.results),
                "total_items": total_items,
                "documented_items": documented_items,
                "overall_coverage": round(overall_coverage, 2),
                "files_with_errors": files_with_errors,
            },
            "files": [r.to_dict() for r in self.results],
        }

    def _empty_report(self, message: str) -> Dict:
        """
        Generate an empty report with an error message.

        Args:
            message: The error message to include.

        Returns:
            Dictionary representing an empty report.
        """
        return {
            "summary": {
                "files_analyzed": 0,
                "total_items": 0,
                "documented_items": 0,
                "overall_coverage": 0.0,
                "files_with_errors": 0,
            },
            "files": [],
            "error": message,
        }

    def export_json(self, report: Dict, output_file: str) -> None:
        """
        Export a report to a JSON file.

        Args:
            report: The report dictionary to export.
            output_file: Path where the JSON file should be saved.
        """
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def export_html(self, report: Dict, output_file: str) -> None:
        """
        Export a report to an HTML file.

        Args:
            report: The report dictionary to export.
            output_file: Path where the HTML file should be saved.
        """
        html_content = self._generate_html(report)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_html(self, report: Dict) -> str:
        """
        Generate HTML content for a report.

        Args:
            report: The report dictionary to convert to HTML.

        Returns:
            HTML string.
        """
        summary = report.get("summary", {})
        files = report.get("files", [])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>docu-pulse Documentation Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card.success {{
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            color: #333;
        }}
        .summary-card.warning {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: #333;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background-color: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .missing-list {{
            background-color: #f8f9fa;
            border-left: 4px solid #e74c3c;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }}
        .coverage-bar {{
            background-color: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            height: 24px;
            display: inline-block;
            width: 100px;
        }}
        .coverage-fill {{
            height: 100%;
            background: linear-gradient(90deg, #e74c3c, #f39c12, #84fab0);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 11px;
            font-weight: bold;
        }}
        .error {{
            background-color: #fadbd8;
            border-left: 4px solid #e74c3c;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
        }}
        footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 docu-pulse Documentation Report</h1>

        <div class="summary">
            <div class="summary-card">
                <h3>Files Analyzed</h3>
                <div class="value">{summary.get('files_analyzed', 0)}</div>
            </div>
            <div class="summary-card success">
                <h3>Overall Coverage</h3>
                <div class="value">{summary.get('overall_coverage', 0):.1f}%</div>
            </div>
            <div class="summary-card success">
                <h3>Documented Items</h3>
                <div class="value">{summary.get('documented_items', 0)}/{summary.get('total_items', 0)}</div>
            </div>
            <div class="summary-card warning">
                <h3>Files with Errors</h3>
                <div class="value">{summary.get('files_with_errors', 0)}</div>
            </div>
        </div>

        <h2>File-by-File Analysis</h2>
        <table>
            <thead>
                <tr>
                    <th>File Path</th>
                    <th>Coverage</th>
                    <th>Documented / Total</th>
                    <th>Missing Docstrings</th>
                </tr>
            </thead>
            <tbody>
"""

        for file_data in files:
            file_path = file_data.get("file_path", "")
            coverage = file_data.get("coverage_percentage", 0)
            documented = file_data.get("documented_items", 0)
            total = file_data.get("total_items", 0)
            errors = file_data.get("errors", [])
            missing = file_data.get("missing_docstrings", [])

            coverage_fill_width = coverage if coverage >= 0 else 0
            coverage_text = f"{coverage:.1f}%" if total > 0 else "N/A"

            missing_html = ""
            if errors:
                for error in errors:
                    missing_html += f'<div class="error">⚠️ {error}</div>'
            elif missing:
                missing_items = ", ".join(
                    [f"{m['name']} ({m['type']})" for m in missing[:3]]
                )
                if len(missing) > 3:
                    missing_items += f", +{len(missing) - 3} more"
                missing_html = f'<div class="missing-list">{missing_items}</div>'

            html += f"""                <tr>
                    <td><code>{file_path}</code></td>
                    <td>
                        <div class="coverage-bar">
                            <div class="coverage-fill" style="width: {coverage_fill_width}%;">
                                {coverage_text}
                            </div>
                        </div>
                    </td>
                    <td>{documented}/{total}</td>
                    <td>{missing_html}</td>
                </tr>
"""

        html += """            </tbody>
        </table>

        <footer>
            <p>Generated by <strong>docu-pulse</strong> — Documentation health analysis tool</p>
            <p>Report generated for comprehensive code documentation auditing and compliance tracking</p>
        </footer>
    </div>
</body>
</html>
"""

        return html
