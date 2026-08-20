import subprocess
import os
import tempfile
from pathlib import Path

from shapeup_scan.detector import detect_projects
from shapeup_scan.models import Project
from shapeup_scan.playwright_check import analyze_page
from shapeup_scan.runner import get_start_command, run_step, start_application
from shapeup_scan.tester import build_test_plan

def scan_repository(repository_url):
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "repo"

        # clone repository from URL with git
        print("Cloning repository from URL:", repository_url)
        
        subprocess.run([
            "git", 
            "clone", 
            repository_url, 
            repo_path], 
            check=True)
        
        print("Clone completed. Scanning the repository for application type...")

        # detect projects in the repository with a maximum depth of 3
        projects = detect_projects(repo_path)

        print(f"Scan completed. Found {len(projects)} project(s) in the repository.")

        for project in projects:
            print(f"Detected project type: {project.type}\nLanguage: {project.language}\nPackage Manager: {project.package_manager}\nProject Root: {project.project_root}")
            if project.evidence and len(project.evidence) > 0:
                print("Evidence found:")

            for evidence in project.evidence or []:
                print(f"- {evidence}")

            report_script_sufficiency(project)

            plan = build_test_plan(project)
            for step in plan:
                result = run_step(step, Path(project.project_root))
                print(f"Step: {result['name']}\nCommand: {result['command']}\nStatus: {result['status']}\nExit Code: {result['exit_code']}\nStdout: {result['stdout']}\nStderr: {result['stderr']}\n")

            run_script = get_start_command(project)

            if run_script:
                print(f"Detected run command: {run_script['command']}. Attempting to run the application...")
                process, server_url = start_application(run_script, Path(project.project_root))

                print(f"Run Command Result:\nStatus: {result['status']}\nExit Code: {result['exit_code']}\nStdout: {result['stdout']}\nStderr: {result['stderr']}\n")

                if server_url:
                    try:
                        print(f"Application started successfully. Analyzing the page at {server_url}...")
                        analysis_result = analyze_page(server_url)  

                        if analysis_result:
                            print("Page analysis completed. Results:")

                            for key, value in analysis_result.items():
                                print(f"{key}: {value}")

                    except Exception as e:
                        print(f"Error during page analysis: {e}")
                else:
                    print("Failed to detect the application URL. Skipping page analysis.")
                    process.terminate()
                    process.wait()
            

def report_script_sufficiency (project: Project): 
    print ("Build support: ", "YES" if project.scripts.get("build") else "NO")
    print ("Test support: ", "YES" if project.scripts.get("test") else "NO")
    print ("Lint support: ", "YES" if project.scripts.get("lint") else "NO")
    print("Overall support: ", "GOOD" if project.scripts.get("build") and project.scripts.get("test") and project.scripts.get("lint") else "NEEDS IMPROVEMENT")
