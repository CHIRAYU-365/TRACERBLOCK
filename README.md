# TRACERBLOCK: Blockchain Supply Chain Portal

## Setup Instructions

Since terminal commands are currently disabled by the environment, please follow these steps to spin up the application manually:

### 1. Database Setup
Ensure PostgreSQL is running locally on port `5432` with username `postgres` and password `password`.
Create a database named `supplychain`:
```bash
createdb -U postgres supplychain
```

### 2. Quick Start (Run Everything Concurrently)
We have added a root `requirements.txt` and a `run_all.py` concurrency script to spin up the entire project—the database migrations, the smart contract deployment, the Django API, and the Streamlit frontend—simultaneously.

Open a terminal in the workspace root, activate your virtual environment, and run:
```bash
pip install -r requirements.txt
python run_all.py
```
This single Python script will orchestrate all the services for you. Press `Ctrl+C` to gracefully shut down the services when you are done.
