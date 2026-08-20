from pathlib import Path


def detect_project(repo: Path) -> dict:

    result = detect_at_path(repo)

    if result["type"] != "unknown":

        return result


    for child in repo.iterdir():

        if child.is_dir() and not child.name.startswith("."):

            result = detect_at_path(child)

            if result["type"] != "unknown":

                result["project_root"] = str(child)

                return result

    return {

        "type": "unknown",
        "language": "unknown",
        "package_manager": "unknown",
        "project_root": str(repo),

    }

def detect_at_path(repo: Path) -> dict:

    if (repo / "package.json").exists():
        return {
            "type": "node",
            "language": "JavaScript/TypeScript",
            "package_manager": detect_node_package_manager(repo),
        }

    if (repo / "pyproject.toml").exists():
        return {
            "type": "python",
            "language": "Python",
            "package_manager": "unknown",
        }

    if (repo / "requirements.txt").exists():
        return {
            "type": "python",
            "language": "Python",
            "package_manager": "pip",
        }

    if (repo / "pom.xml").exists():
        return {
            "type": "maven",
            "language": "Java",
            "package_manager": "Maven",
        }

    if (repo / "build.gradle").exists() or (repo / "build.gradle.kts").exists():
        return {
            "type": "gradle",
            "language": "Java/Kotlin",
            "package_manager": "Gradle",
        }

    if (any(repo.glob("*.sln"))).exists() or (any(repo.glob("*.csproj"))).exists():
        return {
            "type": "dotnet",
            "language": "C#",
            "package_manager": "NuGet",
        }

    return {
        "type": "unknown",
        "language": "unknown",
        "package_manager": "unknown",
    }


def detect_node_package_manager(repo: Path) -> str:

    if (repo / "pnpm-lock.yaml").exists():
        return "pnpm"

    if (repo / "yarn.lock").exists():
        return "yarn"

    if (repo / "package-lock.json").exists():
        return "npm"

    return "npm"