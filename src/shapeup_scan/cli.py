import argparse

from shapeup_scan.scanner import scan_repository


def main():
    parser = argparse.ArgumentParser(
        description="Scan a repository for application quality."
    )

    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a Git repository",
    )

    scan_parser.add_argument(
        "repository",
        help="Git repository URL",
    )

    args = parser.parse_args()

    if args.command == "scan":
        scan_repository(args.repository)
    else:
        parser.print_help()