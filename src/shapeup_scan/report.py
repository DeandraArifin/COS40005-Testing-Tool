from datetime import datetime
from pathlib import Path

from shapeup_scan.models import Project, TestResult


SEPARATOR = "=" * 80
THIN_SEPARATOR = "-" * 80


def default_report_path() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path.cwd() / f"shapeup-scan-report-{stamp}.log"


def write_scan_report(
    path: Path,
    repository_url: str,
    project_reports: list[dict],
    scan_error: str | None = None,
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        format_scan_report(repository_url, project_reports, scan_error=scan_error),
        encoding="utf-8",
    )
    return path


def format_scan_report(
    repository_url: str,
    project_reports: list[dict],
    scan_error: str | None = None,
) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_results = [
        result
        for report in project_reports
        for result in report.get("test_results", [])
    ]
    passed = sum(1 for result in all_results if result.get("status") == "success")
    failed = sum(1 for result in all_results if result.get("status") == "failure")
    skipped = sum(1 for result in all_results if result.get("status") == "skipped")

    lines = [
        SEPARATOR,
        "SHAPEUP SCAN REPORT",
        SEPARATOR,
        f"Generated:   {generated}",
        f"Repository:  {repository_url}",
        f"Projects:    {len(project_reports)}",
        f"Steps run:   {len(all_results)}",
        f"Passed:      {passed}",
        f"Failed:      {failed}",
        f"Skipped:     {skipped}",
        "",
    ]

    if scan_error:
        lines.extend([
            "SCAN ERROR",
            scan_error,
            "",
        ])

    if not project_reports:
        lines.append("No projects were detected in this repository.")
        lines.append("")
    else:
        for index, report in enumerate(project_reports, start=1):
            lines.extend(_format_project_report(index, report))

    lines.extend([
        SEPARATOR,
        "END OF REPORT",
        SEPARATOR,
        "",
    ])
    return "\n".join(lines)


def _format_project_report(index: int, report: dict) -> list[str]:
    project: Project = report["project"]
    support = report.get("script_support", {})
    results: list[TestResult] = report.get("test_results", [])
    playwright = report.get("playwright")
    playwright_error = report.get("playwright_error")
    server_url = report.get("server_url")
    start_command = report.get("start_command")

    lines = [
        SEPARATOR,
        f"PROJECT {index}: {project.project_root}",
        SEPARATOR,
        f"Type:            {project.type}",
        f"Language:        {project.language}",
        f"Package manager: {project.package_manager}",
        f"Evidence:        {', '.join(project.evidence or []) or 'none'}",
        "",
        "Script support",
        f"  Build:   {support.get('build', 'UNKNOWN')}",
        f"  Test:    {support.get('test', 'UNKNOWN')}",
        f"  Lint:    {support.get('lint', 'UNKNOWN')}",
        f"  Overall: {support.get('overall', 'UNKNOWN')}",
        "",
        "Test results",
        THIN_SEPARATOR,
    ]

    if not results:
        lines.append("No test steps were executed for this project.")
        lines.append("")
    else:
        for step_index, result in enumerate(results, start=1):
            lines.extend(_format_test_result(step_index, result))

    lines.extend([
        "Application startup",
        THIN_SEPARATOR,
        f"Start command: {start_command['command'] if start_command else 'not detected'}",
        f"Server URL:    {server_url or 'not detected'}",
        "",
        "Playwright page analysis",
        THIN_SEPARATOR,
    ])

    if playwright_error:
        lines.append(f"Error: {playwright_error}")
        lines.append("")
    elif playwright:
        lines.append(f"Status code:     {playwright.get('status_code')}")
        lines.append(_format_list("Console errors", playwright.get("console_errors") or []))
        lines.append(_format_list("Page errors", playwright.get("page_errors") or []))
        lines.append(_format_list("Failed requests", playwright.get("failed_requests") or []))
        lines.append("")
    else:
        lines.append("Playwright analysis was not run.")
        lines.append("")

    return lines


def _format_test_result(index: int, result: TestResult) -> list[str]:
    output = (result.get("stdout") or "").rstrip()
    stderr = (result.get("stderr") or "").rstrip()
    status = (result.get("status") or "unknown").upper()

    lines = [
        f"[{index}] {result.get('name')}",
        f"Command:   {result.get('command')}",
        f"Status:    {status}",
        f"Exit code: {result.get('exit_code')}",
        "Output:",
    ]

    if output:
        lines.append(output)
    else:
        lines.append("(no output)")

    if stderr:
        lines.append("Stderr:")
        lines.append(stderr)

    lines.append("")
    lines.append(THIN_SEPARATOR)
    lines.append("")
    return lines


def _format_list(title: str, values: list) -> str:
    if not values:
        return f"{title}: none"
    indented = "\n".join(f"  - {value}" for value in values)
    return f"{title}:\n{indented}"
