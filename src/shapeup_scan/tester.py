

from shapeup_scan.models import Project, TestStep


def build_test_plan(project: Project) -> list[TestStep]:
    test_plan = []

    if project.type != "node":
        return []

    return build_node_test_plan(project)

def build_node_test_plan(project: Project) -> list[TestStep]:
    steps = []
    package_manager = project.package_manager
    scripts = project.scripts or {}

    steps.append(TestStep(
        name="Install Dependencies",
        command=f"{package_manager} install",
        description="Install project dependencies"
    ))

    test_scripts = {
        name: command
        for name, command in project.scripts.items()
        if name == "test" or name.startswith("test:")
    }

    for script_name, script_command in test_scripts.items():
        steps.append(TestStep(
            name=f"Run Test: {script_name}",
            command=f"{package_manager} run {script_name}",
            description=f"Run project test script: {script_command}"
        ))

    if(scripts.get("lint")):
        steps.append(TestStep(
            name="Lint Project",
            command=f"{package_manager} run lint",
            description="Run linter on the project"
        ))

    if(scripts.get("build")):
        steps.append(TestStep(
            name="Build Project",
            command=f"{package_manager} run build",
            description="Build the project"
        ))

    steps.append(TestStep(
        name="Analyze Unused Code and Dependencies",
        command=f"npx --yes knip",
        description="Detect unused files, exports, dependencies, and other dead code using Knip"
    ))

    if project.language == "TypeScript":
        steps.append(TestStep(
            name="TypeScript Type Check",
            command="npx tsc --noEmit",
            description="Check the project for TypeScript type errors"
        ))

    return steps
