import os
import shutil
import subprocess
import sys
from pathlib import Path

def remove_packages(dry_run=False):
    print("Removing installed packages...")
    req_file = Path(__file__).parent.parent / "plans" / "requirements.txt"
    if req_file.exists():
        if dry_run:
            print(f"[DRY RUN] Would run: {sys.executable} -m pip uninstall -r {req_file} -y")
            return
        try:
            # Try to uninstall packages listed in requirements.txt
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-r", str(req_file), "-y"], check=True)
            print("Successfully uninstalled packages from plans/requirements.txt")
        except subprocess.CalledProcessError as e:
            print(f"Error uninstalling packages: {e}")
    else:
        print("plans/requirements.txt not found. Skipping package removal.")

def remove_repository(dry_run=False):
    repo_path = Path(__file__).parent.parent.resolve()
    print(f"Preparing to remove repository at: {repo_path}")
    
    if dry_run:
        print(f"[DRY RUN] Would create background script to delete {repo_path}")
        return

    # We can't easily delete the directory we are currently running a script from on Windows
    # without some tricks, but we can try to delete everything else and then 
    # provide instructions or use a batch file.
    
    # For a more thorough cleanup, we'll create a temporary batch file that waits for this process to exit and then deletes the directory.
    if os.name == 'nt': # Windows
        batch_script = repo_path.parent / "cleanup_repo.bat"
        with open(batch_script, "w") as f:
            f.write(f"@echo off\n")
            f.write(f"timeout /t 2 /nobreak > nul\n")
            f.write(f"rd /s /q \"{repo_path}\"\n")
            f.write(f"del \"%~f0\"\n")
        
        print(f"Created cleanup batch script at {batch_script}")
        print("The repository will be fully removed after this script finishes.")
        subprocess.Popen(["cmd.exe", "/c", str(batch_script)], shell=True)
    else: # Linux/Mac
        # On Unix-like systems, we can often delete the directory even if a script is running (though not always recommended)
        # Or use a similar background process trick
        shell_script = repo_path.parent / "cleanup_repo.sh"
        with open(shell_script, "w") as f:
            f.write(f"#!/bin/bash\n")
            f.write(f"sleep 2\n")
            f.write(f"rm -rf \"{repo_path}\"\n")
            f.write(f"rm -- \"$0\"\n")
        
        os.chmod(shell_script, 0o755)
        print(f"Created cleanup shell script at {shell_script}")
        subprocess.Popen(["/bin/bash", str(shell_script)])

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("--- DRY RUN MODE ---")
        remove_packages(dry_run=True)
        remove_repository(dry_run=True)
        sys.exit(0)

    confirm = input("This will uninstall packages and DELETE the repository directory. Are you sure? (y/N): ")
    if confirm.lower() == 'y':
        remove_packages()
        remove_repository()
        print("Cleanup initiated. This window will close, and the directory will be removed.")
    else:
        print("Cleanup cancelled.")
