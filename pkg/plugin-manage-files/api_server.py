# api_server.py
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess

app = FastAPI()

DATA_DIR = "/app/data"

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")

origins = [
    f"http://localhost:5101",
    "https://chat.openai.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create-file")
def create_file(filename: str = Body(...), content: str = Body(...)):
    file_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File already exists")
    with open(file_path, 'w') as file:
        file.write(content)
    return {"message": "File created successfully"}

from pydantic import BaseModel

class GetContentInput(BaseModel):
    path: str

@app.post("/get-content")
def get_content(get_content_input: GetContentInput = Body(...)):
    # Erstelle den absoluten Pfad, indem du den relativen Pfad mit DATA_DIR verbindest
    absolute_path = os.path.join(DATA_DIR, get_content_input.path)
    
    # Überprüfen, ob der Pfad existiert
    if not os.path.exists(absolute_path):
        raise HTTPException(status_code=404, detail="Path not found")
    
    # Wenn der Pfad zu einer Datei führt, gib den Inhalt der Datei zurück
    if os.path.isfile(absolute_path):
        with open(absolute_path, 'r') as file:
            content = file.read()
        return {"content": content}
    
    # Wenn der Pfad zu einem Ordner führt, gib eine Liste der Inhalte zurück
    if os.path.isdir(absolute_path):
        content_list = os.listdir(absolute_path)
        return {"content": content_list}
    
    # Wenn der Pfad weder zu einer Datei noch zu einem Ordner führt, gib einen Fehler zurück
    raise HTTPException(status_code=400, detail="Invalid path")

class Command(BaseModel):
    command: str

@app.post("/run")
def run_command(command: Command = Body(...)):
    try:
        # Trennen Sie den Befehlsstring bei Leerzeichen, um eine Liste von Argumenten zu erstellen
        command_args = command.command.split()
        # Führen Sie das Kommando als Liste von Strings aus, mit shell=False
        result = subprocess.run(command_args, shell=False, check=True, text=True, capture_output=True, cwd=DATA_DIR)
        return {"output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr}
    
class EditFileInput(BaseModel):
    filename: str
    content: str = None
    mode: str
    start_line: int = None
    end_line: int = None
    new_content: str = None

@app.post("/edit-file")
def edit_file(edit_input: EditFileInput = Body(...)):
    file_path = os.path.join(DATA_DIR, edit_input.filename)
    
    # Überprüfen, ob die Datei existiert
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Anhängen von Inhalten an die Datei
    if edit_input.mode == "append":
        with open(file_path, 'a') as file:
            file.write(edit_input.content)
        return {"message": "Content appended successfully"}
    
    # Ändern oder Ersetzen von Inhalten in der Datei
    elif edit_input.mode == "modify":
        if edit_input.start_line is not None and edit_input.new_content is not None:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            end_line = edit_input.end_line if edit_input.end_line is not None else edit_input.start_line
            if edit_input.start_line > len(lines) or end_line > len(lines):
                raise HTTPException(status_code=400, detail="Line number out of range")
            lines[edit_input.start_line - 1 : end_line] = [edit_input.new_content]
            with open(file_path, 'w') as file:
                file.writelines(lines)
            return {"message": "Content modified successfully"}
        else:
            raise HTTPException(status_code=400, detail="Start line and new content are required for modification")
    
    # Ungültiger Modus
    else:
        raise HTTPException(status_code=400, detail="Invalid mode")


