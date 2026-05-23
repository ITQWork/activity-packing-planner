import os
import subprocess
import sys

def stop_site():
    """
    Stops the running FastAPI/Uvicorn application by finding and killing the processes.
    """
    print("--- Attempting to stop the application... ---")
    
    if os.name == 'nt':  # Windows
        # Use taskkill to stop python processes running uvicorn
        # We look for processes that might be our app
        try:
            # Finding processes that are running 'uvicorn' or our 'main.py'
            # Note: This might be broad if other python apps are running, 
            # but usually for local dev this is what's wanted.
            
            # First, try to kill by image name if it's running via uvicorn directly
            subprocess.run(["taskkill", "/F", "/IM", "uvicorn.exe", "/T"], capture_output=True)
            
            # Also try to find python processes that might be running our script
            # We use wmic to be more specific
            cmd = 'wmic process where "commandline like \'%uvicorn%\' or commandline like \'%main.py%\'" get processid'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            pids = [line.strip() for line in result.stdout.splitlines() if line.strip().isdigit()]
            
            for pid in pids:
                if int(pid) != os.getpid(): # Don't kill ourselves
                    print(f"Killing process {pid}...")
                    subprocess.run(["taskkill", "/F", "/PID", pid, "/T"], capture_output=True)
            
            print("--- Stop command executed. ---")
            
        except Exception as e:
            print(f"Error during stop: {e}")
            
    else:  # Unix/macOS
        try:
            # Use pkill to find uvicorn processes
            subprocess.run(["pkill", "-f", "uvicorn"], check=False)
            subprocess.run(["pkill", "-f", "main.py"], check=False)
            print("--- Stop command executed. ---")
        except Exception as e:
            print(f"Error during stop: {e}")

if __name__ == "__main__":
    stop_site()
