from dataclasses import dataclass
from typing import TypedDict

@dataclass
class Project:
    type: str
    language: str
    package_manager: str
    project_root: str
    evidence: list[str] = None
    scripts: dict[str, str] = None

class TestStep(TypedDict):
    name: str
    command: str
    description: str

class TestResult(TypedDict):
    name: str
    command: str
    status: str
    exit_code: int | None
    stdout: str | None
    stderr: str | None
