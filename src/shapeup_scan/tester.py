from pathlib import Path

from shapeup_scan.models import Project, TestStep

PLAYWRIGHT_CONFIG_FILES = (
    "playwright.config.ts",
    "playwright.config.js",
    "playwright.config.mts",
    "playwright.config.mjs",
    "playwright.config.cjs",
)


def build_test_plan(project: Project) -> list[TestStep]:
    if project.type != "node":
        return []

    return build_node_test_plan(project)


def build_node_test_plan(project: Project) -> list[TestStep]:
    steps = []
    package_manager = project.package_manager
    scripts = project.scripts or {}
    root = Path(project.project_root)

    steps.append(TestStep(
        name="Install Dependencies",
        command=f"{package_manager} install",
        description="Install project dependencies"
    ))

    test_scripts = {
        name: command
        for name, command in scripts.items()
        if name == "test" or name.startswith("test:")
    }

    for script_name, script_command in test_scripts.items():
        steps.append(TestStep(
            name=f"Run Test: {script_name}",
            command=f"{package_manager} run {script_name}",
            description=f"Run project test script: {script_command}"
        ))

    if scripts.get("lint"):
        steps.append(TestStep(
            name="Lint Project",
            command=f"{package_manager} run lint",
            description="Run linter on the project"
        ))
    elif not _script_mentions(scripts, "eslint"):
        steps.append(TestStep(
            name="ESLint",
            command="npx --yes eslint .",
            description="Run ESLint on the project"
        ))

    if not _script_mentions(scripts, "jscpd"):
        steps.append(TestStep(
            name="Copy-Paste Detection (jscpd)",
            command=(
                "npx --yes jscpd . "
                '--ignore "**/{node_modules,dist,build,coverage,.git}/**"'
            ),
            description="Detect duplicated code using jscpd"
        ))

    playwright_already_planned = any(
        "playwright" in name.lower() or "playwright" in command.lower()
        for name, command in test_scripts.items()
    )
    if _has_playwright_config(root) and not playwright_already_planned:
        steps.append(TestStep(
            name="Playwright Tests",
            command="npx --yes playwright test",
            description="Run Playwright end-to-end tests"
        ))

    if scripts.get("build"):
        steps.append(TestStep(
            name="Build Project",
            command=f"{package_manager} run build",
            description="Build the project"
        ))

    steps.append(TestStep(
        name="Analyze Unused Code and Dependencies",
        command="npx --yes knip",
        description="Detect unused files, exports, dependencies, and other dead code using Knip"
    ))

    if project.language == "TypeScript":
        steps.append(TestStep(
            name="TypeScript Type Check",
            command="npx tsc --noEmit",
            description="Check the project for TypeScript type errors"
        ))
    return steps


def _script_mentions(scripts: dict[str, str], tool: str) -> bool:
    needle = tool.lower()
    return any(
        needle in name.lower() or needle in command.lower()
        for name, command in scripts.items()
    )


def _has_playwright_config(root: Path) -> bool:
    return any((root / name).exists() for name in PLAYWRIGHT_CONFIG_FILES)

