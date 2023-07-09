import unittest
import requests
import os
import shutil
import subprocess
import time
import uuid

class TestAPIServer(unittest.TestCase):
    BASE_URL = "http://localhost:5003"
    DATA_DIR = "./data/test/"
    SERVER_SCRIPT = "./main.py"  # You need to replace this with the actual path to your main.py script

    def setUp(self):
        # Create the data directory
        os.makedirs(self.DATA_DIR, exist_ok=True)
        
        # Start the server in a new process
        self.server_process = subprocess.Popen(
            ["python", self.SERVER_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Wait for the server to start
        start_time = time.time()
        for line in self.server_process.stdout:
            print(line, end="")
            if "Application startup complete." in line:
                break
            elif time.time() - start_time > 30:  # Timeout after 30 seconds
                raise RuntimeError("Server did not start within 30 seconds")

    def tearDown(self):
        # Terminate the server process
        self.server_process.terminate()
        self.server_process.wait()

        # Close the stdout stream
        self.server_process.stdout.close()

        # Delete the data directory
        shutil.rmtree(self.DATA_DIR)

    def test_create_file(self):
        # Define the test file name and content
        filename = "test/test_file.txt"
        content = "This is a test file."

        # Send a POST request to the create-file endpoint
        response = requests.post(f"{self.BASE_URL}/create-file", json={"filename": filename, "content": content})

        # Check that the status code is 200
        self.assertEqual(response.status_code, 200)

        # Check that the response message is as expected
        self.assertEqual(response.json(), {"message": "File created successfully"})

        # Check that the file was actually created and that its content is as expected
        file_path = os.path.join(self.DATA_DIR, "test_file.txt")
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r") as file:
            self.assertEqual(file.read(), content)

    def test_get_content(self):
        # Generate a unique ID for the file content
        unique_id = str(uuid.uuid4())
        filename = "test/testfile.txt"

        # Create a file with the unique ID as the content
        response = requests.post(
            f"{self.BASE_URL}/create-file", 
            json={"filename": filename, "content": unique_id}
        )
        self.assertEqual(response.status_code, 200)

        # Use the get-content route to get the content of the file
        response = requests.post(
            f"{self.BASE_URL}/get-content", 
            json={"path": filename}
        )
        self.assertEqual(response.status_code, 200)

        # Check that the content of the file is the unique ID
        self.assertEqual(response.json()["content"], unique_id)

    def test_run(self):
        # Create a file in DATA_DIR
        filename = "test/testfile_run.txt"
        response = requests.post(
            f"{self.BASE_URL}/create-file", 
            json={"filename": filename, "content": "test"}
        )
        self.assertEqual(response.status_code, 200)

        # Run the ls command in DATA_DIR
        response = requests.post(
            f"{self.BASE_URL}/run", 
            json={"command": "ls test"}
        )
        self.assertEqual(response.status_code, 200)

        # Check that the output of ls includes the name of the file we created
        self.assertIn("testfile_run.txt", response.json()["output"])

    def test_edit_file(self):
        # Generate a unique ID for the file content
        unique_id = str(uuid.uuid4())
        filename = "test/testfile.txt"

        # Create a file with the unique ID as the content
        response = requests.post(
            f"{self.BASE_URL}/create-file", 
            json={"filename": filename, "content": unique_id}
        )
        self.assertEqual(response.status_code, 200)

        # Use the get-content route to get the content of the file
        response = requests.post(
            f"{self.BASE_URL}/get-content", 
            json={"path": filename}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], unique_id)

        # Generate a new unique ID
        new_unique_id = str(uuid.uuid4())

        # Use the edit-file route to replace the content of the file with the new unique ID
        response = requests.post(
            f"{self.BASE_URL}/edit-file", 
            json={"filename": filename, "new_content": new_unique_id, "mode": "modify", "start_line": 1}
        )
        self.assertEqual(response.status_code, 200)

        # Use the get-content route again to get the new content of the file
        response = requests.post(
            f"{self.BASE_URL}/get-content", 
            json={"path": filename}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], new_unique_id)

# Run the tests
if __name__ == "__main__":
    unittest.main()
