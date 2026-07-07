import subprocess
import time
import sys
import os
import shutil

def run_project():
    print("Starting TRACERBLOCK services concurrently...")
    
    pages_dir = os.path.join(os.path.dirname(__file__), "frontend", "pages")
    if os.path.exists(pages_dir):
        try:
            shutil.rmtree(pages_dir)
        except Exception:
            pass
            
    blockchain_process = subprocess.Popen([sys.executable, "scripts/mock_blockchain.py"])
    time.sleep(1.5)

    subprocess.run([sys.executable, "backend/manage.py", "makemigrations", "supply_chain"])
    subprocess.run([sys.executable, "backend/manage.py", "migrate"])
    
    subprocess.run([sys.executable, "scripts/deploy.py"])

    backend_process = subprocess.Popen([sys.executable, "backend/manage.py", "runserver"])
    time.sleep(3)
    
    frontend_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down TRACERBLOCK services...")
        backend_process.terminate()
        frontend_process.terminate()
        blockchain_process.terminate()
        print("Services stopped.")

if __name__ == "__main__":
    run_project()
