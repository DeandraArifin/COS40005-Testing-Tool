import argparse

from shapeup_scan.demo import run_demo
from shapeup_scan.scanner import scan_repository


def main():
    parser = argparse.ArgumentParser(
        description="Scan a repository for application quality."
    )

    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a Git repository URL or a local project folder",
    )
    scan_parser.add_argument(
        "source",
        help="Git repository URL or local project path",
    )
    scan_parser.add_argument(
        "-o",
        "--output",
        help="Path to write the scan report log file (default: ./shapeup-scan-report-<timestamp>.log)",
    )

    demo_parser = subparsers.add_parser(
        "demo",
        help="Run all bundled test projects and generate report log files",
    )
    demo_parser.add_argument(
        "-o",
        "--output-dir",
        help="Directory for report logs (default: ./reports)",
    )

    args = parser.parse_args()

    if args.command == "scan":
        scan_repository(args.source, output_path=args.output)
    elif args.command == "demo":
        run_demo(output_dir=args.output_dir)
    else:
        parser.print_help()
