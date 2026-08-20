import subprocess
import os
import tempfile

from shapeup_scan.detector import detect_project

def scan_repository(repository_url):
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = os.path.join(temp_dir, "repo")

        print("Cloning repository from URL:", repository_url)
        
        subprocess.run([
            "git", 
            "clone", 
            repository_url, 
            repo_path], 
            check=True)
        
        print("Clone completed. Scanning the repository for application type...")

        project = detect_project(repo_path)