import subprocess
from pathlib import Path

from shapeup_scan.models import Project, TestResult, TestStep


def run_step(step: TestStep, project_root: Path):
    print(f"Running: {step["name"]}")
    print(f"Command: {step["command"]}")

    process = subprocess.Popen(
        step["command"],
        cwd=project_root,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1
    )

    output_lines = []

    assert process.stdout is not None

    try:

        for line in process.stdout:
            print(line, end="", flush=True)
            output_lines.append(line)

    except KeyboardInterrupt:
        process.terminate()
        process.wait()
        raise

    exit_code = process.wait()

    output = "".join(output_lines)

    return TestResult(
        name=step["name"],
        command=step["command"],
        status="success" if exit_code == 0 else "failure",
        exit_code=exit_code,
        stdout=output,
        stderr="",
    )

def get_start_command(project: Project) -> TestStep | None:
    scripts = project.scripts or {}
    package_manager = project.package_manager
    if(scripts.get("dev")):
        return TestStep(
            name="Run Development Server",
            command=f"{package_manager} run dev",
            description="Run the development server for the project"
        )
    elif(scripts.get("start")):
        return TestStep(
            name="Run Start Script",
            command=f"{package_manager} run start",
            description="Run the start script for the project"
        )
    elif(scripts.get("preview")):
        return TestStep(
            name="Run Preview Script",
            command=f"{package_manager} run preview",
            description="Run the preview script for the project"
        )
    return None

def start_application(step: TestStep, root: Path):
    print(f"Starting application with command: {step['command']}")

    process = subprocess.Popen(
        step["command"],
        cwd=root,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert process.stdout is not None

    server_url = None

    for line in process.stdout:
        print(line, end="", flush=True)

        for token in line.split():

            cleaned_token = token.strip().rstrip("/.,")

            if (
                cleaned_token.startswith("http://localhost:")
                or cleaned_token.startswith("http://127.0.0.1:")
            ):
                server_url = cleaned_token
                break

        if server_url:
            break

        if process.poll() is not None:
            break

    return process, server_url