import subprocess
import os
import tempfile
from pathlib import Path

from shapeup_scan.detector import detect_projects

def scan_repository(repository_url):
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "repo"

        print("Cloning repository from URL:", repository_url)
        
        subprocess.run([
            "git", 
            "clone", 
            repository_url, 
            repo_path], 
            check=True)
        
        print("Clone completed. Scanning the repository for application type...")

        projects = detect_projects(repo_path)

        print(f"Scan completed. Found {len(projects)} project(s) in the repository.")

        for project in projects:
            print(f"Detected project type: {project.type}\nLanguage: {project.language}\nPackage Manager: {project.package_manager}\nProject Root: {project.project_root}")
            if project.evidence and len(project.evidence) > 0:
                print("Evidence found:")
            for evidence in project.evidence or []:
                print(f"- {evidence}")