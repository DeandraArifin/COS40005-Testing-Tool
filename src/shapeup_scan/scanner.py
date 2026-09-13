import shutil
import subprocess
import tempfile
from pathlib import Path

from shapeup_scan.detector import detect_projects
from shapeup_scan.models import Project, TestResult
from shapeup_scan.playwright_check import analyze_page
from shapeup_scan.report import default_report_path, write_scan_report
from shapeup_scan.runner import get_start_command, run_step, start_application
from shapeup_scan.tester import build_test_plan


def scan_repository(source, output_path=None):
    report_path = Path(output_path) if output_path else default_report_path()
    project_reports = []
    scan_error = None
    source_label = str(source)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "repo"
            source_label = prepare_workspace(source, repo_path)

            print("Workspace ready. Scanning for application type...")

            projects = detect_projects(repo_path)

            print(f"Scan completed. Found {len(projects)} project(s).")

            for project in projects:
                project_reports.append(_scan_project(project))
    except Exception as error:
        scan_error = str(error)
        raise
    finally:
        saved_path = write_scan_report(
            report_path,
            source_label,
            project_reports,
            scan_error=scan_error,
        )
        print(f"\nScan report saved to: {saved_path.resolve()}")
        print("You can download or copy that log file to keep a record of every test and its output.")

    return report_path


def prepare_workspace(source, dest: Path) -> str:
    local_path = Path(source).expanduser()
    if local_path.exists() and local_path.is_dir():
        resolved = local_path.resolve()
        print("Using local project:", resolved)
        shutil.copytree(
            resolved,
            dest,
            ignore=shutil.ignore_patterns(
                "node_modules",
                ".git",
                "dist",
                "build",
                "coverage",
                ".venv",
                "venv",
            ),
        )
        return str(resolved)

    print("Cloning repository from URL:", source)
    subprocess.run(["git", "clone", source, dest], check=True)
    print("Clone completed.")
    return str(source)


def _scan_project(project: Project) -> dict:
    print(
        f"Detected project type: {project.type}\n"
        f"Language: {project.language}\n"
        f"Package Manager: {project.package_manager}\n"
        f"Project Root: {project.project_root}"
    )

    if project.evidence:
        print("Evidence found:")
        for evidence in project.evidence:
            print(f"- {evidence}")

    script_support = get_script_support(project)
    report_script_sufficiency(script_support)

    test_results: list[TestResult] = []
    root = Path(project.project_root)

    for step in build_test_plan(project):
        result = run_step(step, root)
        test_results.append(result)
        print(
            f"Step: {result['name']}\n"
            f"Command: {result['command']}\n"
            f"Status: {result['status']}\n"
            f"Exit Code: {result['exit_code']}\n"
            f"Stdout: {result['stdout']}\n"
            f"Stderr: {result['stderr']}\n"
        )

    run_script = get_start_command(project)
    server_url = None
    playwright = None
    playwright_error = None

    if run_script:
        print(f"Detected run command: {run_script['command']}. Attempting to run the application...")
        process = None
        try:
            process, server_url = start_application(run_script, root)

            if server_url:
                try:
                    print(f"Application started successfully. Analyzing the page at {server_url}...")
                    playwright = analyze_page(server_url)

                    if playwright:
                        print("Page analysis completed. Results:")
                        for key, value in playwright.items():
                            print(f"{key}: {value}")

                    test_results.append(_playwright_result(server_url, playwright))
                except Exception as e:
                    playwright_error = str(e)
                    print(f"Error during page analysis: {e}")
                    test_results.append(TestResult(
                        name="Playwright Page Analysis",
                        command=f"playwright analyze {server_url}",
                        status="failure",
                        exit_code=1,
                        stdout="",
                        stderr=playwright_error,
                    ))
            else:
                print("Failed to detect the application URL. Skipping page analysis.")
                test_results.append(TestResult(
                    name="Playwright Page Analysis",
                    command="playwright analyze",
                    status="skipped",
                    exit_code=None,
                    stdout="",
                    stderr="Application URL was not detected.",
                ))
        finally:
            if process is not None:
                process.terminate()
                process.wait()
    else:
        test_results.append(TestResult(
            name="Playwright Page Analysis",
            command="playwright analyze",
            status="skipped",
            exit_code=None,
            stdout="",
            stderr="No start/dev/preview script was detected.",
        ))

    return {
        "project": project,
        "script_support": script_support,
        "test_results": test_results,
        "start_command": run_script,
        "server_url": server_url,
        "playwright": playwright,
        "playwright_error": playwright_error,
    }


def get_script_support(project: Project) -> dict[str, str]:
    scripts = project.scripts or {}
    build = "YES" if scripts.get("build") else "NO"
    test = "YES" if scripts.get("test") else "NO"
    lint = "YES" if scripts.get("lint") else "NO"
    overall = (
        "GOOD"
        if scripts.get("build") and scripts.get("test") and scripts.get("lint")
        else "NEEDS IMPROVEMENT"
    )
    return {
        "build": build,
        "test": test,
        "lint": lint,
        "overall": overall,
    }


def report_script_sufficiency(support: dict[str, str]):
    print("Build support: ", support["build"])
    print("Test support: ", support["test"])
    print("Lint support: ", support["lint"])
    print("Overall support: ", support["overall"])


def _playwright_result(server_url: str, analysis: dict) -> TestResult:
    console_errors = analysis.get("console_errors") or []
    page_errors = analysis.get("page_errors") or []
    failed_requests = analysis.get("failed_requests") or []
    status_code = analysis.get("status_code")

    healthy = (
        status_code is not None
        and 200 <= status_code < 400
        and not console_errors
        and not page_errors
        and not failed_requests
    )

    output_lines = [
        f"URL: {server_url}",
        f"Status code: {status_code}",
        f"Console errors: {console_errors or 'none'}",
        f"Page errors: {page_errors or 'none'}",
        f"Failed requests: {failed_requests or 'none'}",
    ]

    return TestResult(
        name="Playwright Page Analysis",
        command=f"playwright analyze {server_url}",
        status="success" if healthy else "failure",
        exit_code=0 if healthy else 1,
        stdout="\n".join(output_lines) + "\n",
        stderr="",
    )
