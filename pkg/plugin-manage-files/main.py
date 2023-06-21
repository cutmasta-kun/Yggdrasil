# main.py
import subprocess

# Starten von Flask-Server in einem Subprozess
subprocess.run(["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "5003", "--reload"])