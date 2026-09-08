"""
Command-line interface for docu-pulse.

Provides the CLI tool for analyzing Python repositories for documentation
completeness and generating health reports in multiple formats.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from docupulse.core import DocumentationAnalyzer
from docupulse import __version__


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for docu-pulse.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="docu-pulse",
        description="Lightweight CLI utility for code quality and documentation analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  docu-pulse /path/to/project
  docu-pulse . --include-private --output report.json
  docu-pulse src/ --html report.html
  docu-pulse . --min-coverage 80

For more information, visit: https://github.com/yourusername/docu-pulse
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the directory or file to analyze (default: current directory)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version number and exit",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Output file for JSON report (default: print to stdout)",
    )

    parser.add_argument(
        "--html",
        metavar="FILE",
        help="Export analysis as HTML report",
    )

    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include private methods and functions in analysis",
    )

    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include test files in analysis",
    )

    parser.add_argument(
        "--min-coverage",
        type=float,
        metavar="PERCENT",
        help="Exit with error code 1 if overall coverage is below this percentage",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress standard output (only show errors)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print detailed analysis for each file",
    )

    return parser


def format_summary(report: dict, verbose: bool = False) -> str:
    """
    Format the analysis report for console output.

    Args:
        report: The analysis report dictionary.
        verbose: If True, include detailed file information.

    Returns:
        Formatted string for console output.
    """
    summary = report.get("summary", {})
    files = report.get("files", [])

    output = []
    output.append("\n" + "=" * 70)
    output.append("📊  docu-pulse - Documentation Health Report")
    output.append("=" * 70)

    output.append(f"\n📁 Files Analyzed:        {summary.get('files_analyzed', 0)}")
    output.append(f"📝 Total Items:           {summary.get('total_items', 0)}")
    output.append(f"✅ Documented Items:      {summary.get('documented_items', 0)}")
    output.append(
        f"📈 Overall Coverage:      {summary.get('overall_coverage', 0):.2f}%"
    )
    output.append(f"⚠️  Files with Errors:     {summary.get('files_with_errors', 0)}")

    if verbose and files:
        output.append("\n" + "-" * 70)
        output.append("Detailed File Analysis:")
        output.append("-" * 70)

        for file_data in files:
            file_path = file_data.get("file_path", "")
            coverage = file_data.get("coverage_percentage", 0)
            documented = file_data.get("documented_items", 0)
            total = file_data.get("total_items", 0)
            errors = file_data.get("errors", [])
            missing = file_data.get("missing_docstrings", [])

            output.append(f"\n📄 {file_path}")
            output.append(f"   Coverage: {coverage:.2f}% ({documented}/{total})")

            if errors:
                for error in errors:
                    output.append(f"   ❌ Error: {error}")

            if missing:
                output.append(f"   Missing docstrings ({len(missing)}):")
                for item in missing[:5]:
                    output.append(
                        f"      • {item['name']} ({item['type']}) at line {item['line']}"
                    )
                if len(missing) > 5:
                    output.append(f"      ... and {len(missing) - 5} more")

    output.append("\n" + "=" * 70 + "\n")

    return "\n".join(output)


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for the docu-pulse CLI.

    Args:
        argv: Command-line arguments (for testing). If None, uses sys.argv[1:].

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    target_path = args.path
    ignore_private = not args.include_private
    ignore_tests = not args.include_tests

    target_path_obj = Path(target_path)

    if not target_path_obj.exists():
        if not args.quiet:
            print(f"❌ Error: Path '{target_path}' does not exist", file=sys.stderr)
        return 1

    analyzer = DocumentationAnalyzer(
        ignore_private=ignore_private, ignore_tests=ignore_tests
    )

    if target_path_obj.is_file() and target_path_obj.suffix == ".py":
        report = {"summary": {}, "files": []}
        result = analyzer.analyze_file(target_path)
        if result:
            report["summary"] = {
                "files_analyzed": 1,
                "total_items": result.total_items,
                "documented_items": result.documented_items,
                "overall_coverage": result.coverage_percentage,
                "files_with_errors": 1 if result.errors else 0,
            }
            report["files"] = [result.to_dict()]
    else:
        report = analyzer.analyze_directory(target_path)

    if "error" in report and report.get("summary", {}).get("files_analyzed", 0) == 0:
        if not args.quiet:
            print(f"❌ Error: {report['error']}", file=sys.stderr)
        return 1

    if args.output:
        try:
            analyzer.export_json(report, args.output)
            if not args.quiet:
                print(f"✅ JSON report saved to: {args.output}")
        except IOError as e:
            print(f"❌ Error writing JSON file: {e}", file=sys.stderr)
            return 1

    if args.html:
        try:
            analyzer.export_html(report, args.html)
            if not args.quiet:
                print(f"✅ HTML report saved to: {args.html}")
        except IOError as e:
            print(f"❌ Error writing HTML file: {e}", file=sys.stderr)
            return 1

    if not args.quiet:
        print(format_summary(report, verbose=args.verbose))

    coverage = report.get("summary", {}).get("overall_coverage", 0)
    if args.min_coverage and coverage < args.min_coverage:
        if not args.quiet:
            print(
                f"❌ Coverage {coverage:.2f}% is below minimum required {args.min_coverage:.2f}%",
                file=sys.stderr,
            )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
