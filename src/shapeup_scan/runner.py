import subprocess
from pathlib import Path

from shapeup_scan.models import TestResult, TestStep


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