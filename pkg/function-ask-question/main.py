# main.py
import subprocess

if __name__ == "__main__":
    # Run the API server and block until it's finished
    server_process = subprocess.run(["python", "api_server.py"])
