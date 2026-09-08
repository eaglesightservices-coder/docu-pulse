"""
Unit tests for docupulse.core module.

Tests the DocumentationAnalyzer class and related functionality including
file parsing, docstring detection, coverage calculation, and report generation.
"""

import tempfile
import os
from pathlib import Path
import pytest

from docupulse.core import DocumentationAnalyzer, AnalysisResult


class TestAnalysisResult:
    """Tests for the AnalysisResult dataclass."""

    def test_analysis_result_creation(self):
        """Test creating an AnalysisResult instance."""
        result = AnalysisResult(
            file_path="/path/to/file.py",
            total_items=10,
            documented_items=8,
            coverage_percentage=80.0,
            missing_docstrings=[{"name": "foo", "type": "function", "line": 5}],
            errors=[],
        )

        assert result.file_path == "/path/to/file.py"
        assert result.total_items == 10
        assert result.documented_items == 8
        assert result.coverage_percentage == 80.0
        assert len(result.missing_docstrings) == 1
        assert len(result.errors) == 0

    def test_analysis_result_to_dict(self):
        """Test converting AnalysisResult to dictionary."""
        result = AnalysisResult(
            file_path="/path/to/file.py",
            total_items=5,
            documented_items=3,
            coverage_percentage=60.0,
            missing_docstrings=[],
            errors=[],
        )

        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert result_dict["file_path"] == "/path/to/file.py"
        assert result_dict["total_items"] == 5
        assert result_dict["coverage_percentage"] == 60.0


class TestDocumentationAnalyzer:
    """Tests for the DocumentationAnalyzer class."""

    def test_analyzer_initialization(self):
        """Test creating a DocumentationAnalyzer instance."""
        analyzer = DocumentationAnalyzer(ignore_private=True, ignore_tests=True)

        assert analyzer.ignore_private is True
        assert analyzer.ignore_tests is True
        assert analyzer.results == []

    def test_analyzer_with_custom_config(self):
        """Test analyzer with custom configuration."""
        analyzer = DocumentationAnalyzer(ignore_private=False, ignore_tests=False)

        assert analyzer.ignore_private is False
        assert analyzer.ignore_tests is False

    def test_analyze_file_with_docstrings(self):
        """Test analyzing a file with properly documented functions."""
        code = '''
"""Module docstring."""

def documented_function():
    """This function is documented."""
    pass

class DocumentedClass:
    """This class is documented."""

    def documented_method(self):
        """This method is documented."""
        pass
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="."
        ) as f:
            f.write(code)
            f.flush()
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer()
            result = analyzer.analyze_file(temp_file)

            assert result.total_items >= 3
            assert result.documented_items >= 3
            assert result.coverage_percentage >= 90.0
            assert len(result.errors) == 0
        finally:
            os.unlink(temp_file)

    def test_analyze_file_with_missing_docstrings(self):
        """Test analyzing a file with missing docstrings."""
        code = '''
def undocumented_function():
    pass

class UndocumentedClass:
    def undocumented_method(self):
        pass
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="."
        ) as f:
            f.write(code)
            f.flush()
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer()
            result = analyzer.analyze_file(temp_file)

            assert result.total_items == 3
            assert result.documented_items == 0
            assert result.coverage_percentage == 0.0
            assert len(result.missing_docstrings) == 3
        finally:
            os.unlink(temp_file)

    def test_analyze_file_partial_documentation(self):
        """Test analyzing a file with partial documentation."""
        code = '''
def documented_func():
    """This is documented."""
    pass

def undocumented_func():
    pass

class PartialClass:
    """Class is documented."""

    def undocumented_method(self):
        pass
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="."
        ) as f:
            f.write(code)
            f.flush()
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer()
            result = analyzer.analyze_file(temp_file)

            assert result.total_items == 4
            assert result.documented_items == 2
            assert result.coverage_percentage == 50.0
            assert len(result.missing_docstrings) == 2
        finally:
            os.unlink(temp_file)

    def test_analyze_file_with_private_methods(self):
        """Test that private methods are ignored by default."""
        code = '''
def public_function():
    """Public function."""
    pass

def _private_function():
    pass

class PublicClass:
    """Public class."""

    def public_method(self):
        """Public method."""
        pass

    def _private_method(self):
        pass
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="."
        ) as f:
            f.write(code)
            f.flush()
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer(ignore_private=True)
            result = analyzer.analyze_file(temp_file)

            assert result.total_items == 3
            assert result.documented_items == 3
            assert result.coverage_percentage == 100.0
        finally:
            os.unlink(temp_file)

    def test_analyze_file_include_private_methods(self):
        """Test including private methods in analysis."""
        code = '''
def _private_function():
    pass
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="."
        ) as f:
            f.write(code)
            f.flush()
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer(ignore_private=False)
            result = analyzer.analyze_file(temp_file)

            assert result.total_items == 1
            assert result.documented_items == 0
        finally:
            os.unlink(temp_file)

    def test_analyze_file_with_syntax_error(self):
        """Test handling of files with syntax errors."""
        code = '''
def broken_function(
    pass
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="."
        ) as f:
            f.write(code)
            f.flush()
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer()
            result = analyzer.analyze_file(temp_file)

            assert result.total_items == 0
            assert result.documented_items == 0
            assert len(result.errors) > 0
        finally:
            os.unlink(temp_file)

    def test_analyze_nonexistent_file(self):
        """Test analyzing a file that doesn't exist."""
        analyzer = DocumentationAnalyzer()
        result = analyzer.analyze_file("/nonexistent/file.py")

        assert result.total_items == 0
        assert result.documented_items == 0
        assert len(result.errors) > 0

    def test_analyze_directory(self):
        """Test analyzing a directory with multiple files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = Path(temp_dir) / "file1.py"
            file1.write_text(
                '''
def documented():
    """Documented."""
    pass
'''
            )

            file2 = Path(temp_dir) / "file2.py"
            file2.write_text(
                '''
def undocumented():
    pass
'''
            )

            analyzer = DocumentationAnalyzer()
            report = analyzer.analyze_directory(temp_dir)

            assert report["summary"]["files_analyzed"] == 2
            assert report["summary"]["total_items"] == 2
            assert report["summary"]["documented_items"] == 1
            assert report["summary"]["overall_coverage"] == 50.0
            assert len(report["files"]) == 2

    def test_analyze_directory_skips_test_files(self):
        """Test that test files are skipped by default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            src_file = Path(temp_dir) / "main.py"
            src_file.write_text(
                '''
def function():
    pass
'''
            )

            test_file = Path(temp_dir) / "test_main.py"
            test_file.write_text(
                '''
def test_function():
    pass
'''
            )

            analyzer = DocumentationAnalyzer(ignore_tests=True)
            report = analyzer.analyze_directory(temp_dir)

            assert report["summary"]["files_analyzed"] == 1
            assert len(report["files"]) == 1

    def test_analyze_directory_includes_test_files(self):
        """Test including test files in analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            src_file = Path(temp_dir) / "main.py"
            src_file.write_text(
                '''
def function():
    pass
'''
            )

            test_file = Path(temp_dir) / "test_main.py"
            test_file.write_text(
                '''
def test_function():
    pass
'''
            )

            analyzer = DocumentationAnalyzer(ignore_tests=False)
            report = analyzer.analyze_directory(temp_dir)

            assert report["summary"]["files_analyzed"] == 2
            assert len(report["files"]) == 2

    def test_analyze_nonexistent_directory(self):
        """Test analyzing a directory that doesn't exist."""
        analyzer = DocumentationAnalyzer()
        report = analyzer.analyze_directory("/nonexistent/directory")

        assert report["summary"]["files_analyzed"] == 0
        assert "error" in report

    def test_analyze_directory_with_no_python_files(self):
        """Test analyzing a directory with no Python files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir).joinpath("file.txt").write_text("not python")

            analyzer = DocumentationAnalyzer()
            report = analyzer.analyze_directory(temp_dir)

            assert report["summary"]["files_analyzed"] == 0
            assert "error" in report

    def test_export_json(self):
        """Test exporting report to JSON."""
        report = {
            "summary": {
                "files_analyzed": 1,
                "total_items": 5,
                "documented_items": 3,
                "overall_coverage": 60.0,
                "files_with_errors": 0,
            },
            "files": [],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, dir="."
        ) as f:
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer()
            analyzer.export_json(report, temp_file)

            assert os.path.exists(temp_file)
            with open(temp_file, "r") as f:
                content = f.read()
                assert "files_analyzed" in content
                assert "60.0" in content
        finally:
            os.unlink(temp_file)

    def test_export_html(self):
        """Test exporting report to HTML."""
        report = {
            "summary": {
                "files_analyzed": 1,
                "total_items": 5,
                "documented_items": 3,
                "overall_coverage": 60.0,
                "files_with_errors": 0,
            },
            "files": [],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, dir="."
        ) as f:
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer()
            analyzer.export_html(report, temp_file)

            assert os.path.exists(temp_file)
            with open(temp_file, "r") as f:
                content = f.read()
                assert "<!DOCTYPE html>" in content
                assert "docu-pulse" in content
                assert "60.0" in content
        finally:
            os.unlink(temp_file)

    def test_async_functions_are_detected(self):
        """Test that async functions are properly detected."""
        code = '''
async def async_function():
    pass

async def documented_async():
    """Documented async function."""
    pass
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="."
        ) as f:
            f.write(code)
            f.flush()
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer()
            result = analyzer.analyze_file(temp_file)

            assert result.total_items == 2
            assert result.documented_items == 1
        finally:
            os.unlink(temp_file)

    def test_coverage_calculation_accuracy(self):
        """Test accurate coverage calculation."""
        code = '''
def func1():
    """Documented."""
    pass

def func2():
    pass

def func3():
    """Documented."""
    pass

def func4():
    pass

def func5():
    pass
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="."
        ) as f:
            f.write(code)
            f.flush()
            temp_file = f.name

        try:
            analyzer = DocumentationAnalyzer()
            result = analyzer.analyze_file(temp_file)

            assert result.total_items == 5
            assert result.documented_items == 2
            assert result.coverage_percentage == 40.0
        finally:
            os.unlink(temp_file)
