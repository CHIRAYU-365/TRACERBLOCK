import subprocess
import time
import sys

def run_project():
    print("Starting TRACERBLOCK services concurrently...")
    
    # 1. Run Migrations
    print("Running Django migrations...")
    subprocess.run([sys.executable, "backend/manage.py", "makemigrations", "supply_chain"])
    subprocess.run([sys.executable, "backend/manage.py", "migrate"])
    
    # 2. Deploy Contracts
    print("Deploying smart contracts...")
    subprocess.run([sys.executable, "scripts/deploy.py"])

    # 3. Start Django Backend
    print("Starting Django backend...")
    backend_process = subprocess.Popen([sys.executable, "backend/manage.py", "runserver"])
    
    # Wait 3 seconds to ensure API is ready
    time.sleep(3)
    
    # 4. Start Streamlit Frontend
    print("Starting Streamlit frontend...")
    frontend_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])
    
    try:
        # Wait for processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down TRACERBLOCK services...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Services stopped.")

if __name__ == "__main__":
    run_project()
