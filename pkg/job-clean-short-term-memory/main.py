# main.py
import subprocess

if __name__ == "__main__":
    # Start the deamon process in the background
    deamon_process = subprocess.Popen(["python", "deamon.py"])

    # Run the API server and block until it's finished
    server_process = subprocess.run(["python", "api_server.py"])
