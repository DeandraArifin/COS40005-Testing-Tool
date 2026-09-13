from datetime import datetime
from pathlib import Path

from shapeup_scan.report import SEPARATOR
from shapeup_scan.scanner import scan_repository


def examples_root() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "examples"


def list_example_projects() -> list[Path]:
    root = examples_root()
    if not root.exists():
        return []
    return sorted(
        path for path in root.iterdir()
        if path.is_dir() and (path / "package.json").exists()
    )


def run_demo(output_dir=None) -> Path:
    examples = list_example_projects()
    if not examples:
        raise FileNotFoundError(
            f"No demo projects found in {examples_root()}. "
            "Run this command from the COS40005-Testing-Tool repo."
        )

    reports_dir = Path(output_dir) if output_dir else Path.cwd() / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    print(SEPARATOR)
    print("SHAPEUP DEMO")
    print(SEPARATOR)
    print(f"Found {len(examples)} test project(s).")
    print("Each project will be scanned, then a log report will be written.")
    print()

    results = []
    for index, example in enumerate(examples, start=1):
        report_path = reports_dir / f"{example.name}.log"
        print(SEPARATOR)
        print(f"[{index}/{len(examples)}] Scanning {example.name}")
        print(SEPARATOR)
        error = None
        try:
            scan_repository(example, output_path=report_path)
        except Exception as exc:
            error = str(exc)
            print(f"Scan finished with an error for {example.name}: {exc}")
        results.append((example.name, report_path, error))
        print()

    summary_path = reports_dir / "all-projects.log"
    summary_path.write_text(_format_demo_summary(results), encoding="utf-8")

    print(SEPARATOR)
    print("DEMO COMPLETE")
    print(SEPARATOR)
    for name, report_path, error in results:
        status = "ERROR" if error else "DONE"
        print(f"  [{status}] {name}: {report_path.resolve()}")
    print(f"  Combined log: {summary_path.resolve()}")
    print()
    print("Open those .log files to present the test output.")
    return summary_path


def _format_demo_summary(results: list[tuple[str, Path, str | None]]) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        SEPARATOR,
        "SHAPEUP DEMO SUMMARY",
        SEPARATOR,
        f"Generated: {generated}",
        f"Projects:  {len(results)}",
        "",
    ]
    for name, report_path, error in results:
        lines.append(THIN)
        lines.append(f"Project: {name}")
        lines.append(f"Report:  {report_path.resolve()}")
        lines.append(f"Status:  {'FAILED TO COMPLETE' if error else 'COMPLETED'}")
        if error:
            lines.append(f"Error:   {error}")
        if report_path.exists():
            lines.append("")
            lines.append(report_path.read_text(encoding="utf-8").rstrip())
            lines.append("")
    lines.extend([SEPARATOR, "END OF DEMO SUMMARY", SEPARATOR, ""])
    return "\n".join(lines)


THIN = "-" * 80
