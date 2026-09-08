"""
docu-pulse: Lightweight CLI utility for code quality and documentation analysis.

A modular tool that analyzes repositories for docstring completeness,
API documentation gaps, and generates automated health reports.
"""

__version__ = "0.1.0"
__author__ = "docu-pulse Contributors"
__license__ = "MIT"

from docupulse.core import DocumentationAnalyzer, AnalysisResult

__all__ = ["DocumentationAnalyzer", "AnalysisResult", "__version__"]
