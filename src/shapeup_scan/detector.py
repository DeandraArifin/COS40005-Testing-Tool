from pathlib import Path
from shapeup_scan.models import Project

IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "vendor",
    "target",
}



def find_candidate_directories(repo: Path, max_depth: int = 3):

    candidates = [repo]

    for path in repo.rglob("*"):

        if not path.is_dir():
            continue

        relative = path.relative_to(repo)

        if any(part in IGNORE_DIRS for part in relative.parts):
            continue

        if len(relative.parts) > max_depth:
            continue

        candidates.append(path)

    return candidates


def detect_projects(repo: Path) -> list[Project]:

    candidates = find_candidate_directories(repo)
    projects = []

    for candidate in candidates:
        project = detect_at_path(candidate)

        if project.type != "unknown":
            project.project_root = str(candidate)
            projects.append(project)

    return projects

def detect_at_path(repo: Path) -> Project:

    if (repo / "package.json").exists() or (repo/"package-lock.json").exists() or (repo / "yarn.lock").exists() or (repo / "pnpm-lock.yaml").exists():
        return Project (
            type="node",
            language="JavaScript/TypeScript",
            package_manager=detect_node_package_manager(repo),
            project_root=str(repo),
            evidence=detect_evidence(["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"], repo)
        )

    if (repo / "pyproject.toml").exists() or (repo / "setup.py").exists() or (repo / "Pipfile").exists():
        return Project (
            type="python",
            language="Python",
            package_manager="unknown",
            project_root=str(repo),
            evidence=detect_evidence(["pyproject.toml", "setup.py", "Pipfile"], repo)
        )

    if (repo / "requirements.txt").exists():
        return Project (
            type="python",
            language="Python",
            package_manager="pip",
            project_root=str(repo),
            evidence=detect_evidence(["requirements.txt"], repo)
        )

    if (repo / "pom.xml").exists():
        return Project (
            type="maven",
            language="Java",
            package_manager="Maven",
            project_root=str(repo),
            evidence=detect_evidence(["pom.xml"], repo)
        )

    if (repo / "build.gradle").exists() or (repo / "build.gradle.kts").exists():
        return Project (
            type="gradle",
            language="Java/Kotlin",
            package_manager="Gradle",
            project_root=str(repo),
            evidence=detect_evidence(["build.gradle", "build.gradle.kts"], repo)
        )

    if (any(repo.glob("*.sln"))) or (any(repo.glob("*.csproj"))):
        return Project (
            type="dotnet",
            language="C#",
            package_manager="NuGet",
            project_root=str(repo),
            evidence=detect_evidence([str(p.relative_to(repo)) for p in repo.glob("*.sln")] + [str(p.relative_to(repo)) for p in repo.glob("*.csproj")], repo)
        )

    if (repo/"Gemfile").exists() or (repo/"Gemfile.lock").exists():
        return Project (
            type="ruby",
            language="Ruby",
            package_manager="Bundler",
            project_root=str(repo),
            evidence=detect_evidence(["Gemfile", "Gemfile.lock"], repo)
        )

    if (repo / "Package.swift").exists() or (repo / "Cartfile").exists() or (repo / "Podfile").exists() or (any(repo.glob("*.xcodeproj"))):
        return Project (
            type="ios",
            language="Swift/Objective-C",
            package_manager=detect_swift_package_manager(repo),
            project_root=str(repo),
            evidence=detect_evidence(["Package.swift", "Cartfile", "Podfile"] + [str(p.relative_to(repo)) for p in repo.glob("*.xcodeproj")], repo)
        )

    if (repo / "Cargo.toml").exists() or (repo / "Cargo.lock").exists():
        return Project (
            type="rust",
            language="Rust",
            package_manager="Cargo",
            project_root=str(repo),
            evidence=detect_evidence(["Cargo.toml", "Cargo.lock"], repo)
        )

    if (repo / "go.mod").exists() or (repo / "go.sum").exists():
        return Project (
            type="go",
            language="Go",
            package_manager="Go Modules",
            project_root=str(repo),
            evidence=detect_evidence(["go.mod", "go.sum"], repo)
        )

    if (repo / "pubspec.yaml").exists() or (repo / "pubspec.lock").exists():
        return Project (
            type="flutter",
            language="Dart",
            package_manager="Pub",
            project_root=str(repo),
            evidence=detect_evidence(["pubspec.yaml", "pubspec.lock"], repo)
        )

    if (repo / "mix.exs").exists() or (repo / "mix.lock").exists():
        return Project (
            type="elixir",
            language="Elixir",
            package_manager="Mix",
            project_root=str(repo),
            evidence=detect_evidence(["mix.exs", "mix.lock"], repo)
        )
        

    return Project (
        type="unknown",
        language="unknown",
        package_manager="unknown",
        project_root=str(repo),
        evidence=[]
    )

def detect_evidence(list: list[str], repo: Path) -> list[str]:
    evidence = []
    for item in list:
        if (repo / item).exists():
            evidence.append(str(item))

    return evidence

def detect_node_package_manager(repo: Path) -> str:

    if (repo / "pnpm-lock.yaml").exists():
        return "pnpm"

    if (repo / "yarn.lock").exists():
        return "yarn"

    if (repo / "package-lock.json").exists():
        return "npm"

    return "npm"

def detect_swift_package_manager(repo: Path) -> str:

    if (repo / "Package.swift").exists():
        return "Swift Package Manager"

    if (repo / "Cartfile").exists():
        return "Carthage"

    if (repo / "Podfile").exists():
        return "CocoaPods"

    return "unknown"