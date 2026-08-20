from dataclasses import dataclass

@dataclass
class Project:
    type: str
    language: str
    package_manager: str
    project_root: str
    evidence: list[str] = None