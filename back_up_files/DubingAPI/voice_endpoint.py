from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from app.routers.voice_module import VoiceSynthesizer
import os

app = FastAPI()
voice_synthesizer = VoiceSynthesizer()
templates = Jinja2Templates(directory="../templates/Dubing")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dubing.html", {"request": request})

@app.post("/generate-audio/")
async def generate_audio(voice: str = Form(...), script: str = Form(...)):
    filename, audio_url = voice_synthesizer.generate_audio_file(voice, script)
    return {"filename": filename, "audio_url": audio_url}

@app.get("/download-audio/{filename}")
async def download_audio(filename: str):
    audio_file_path = os.path.join(voice_synthesizer.audio_files_directory, filename)
    return FileResponse(path=audio_file_path, media_type='audio/mp3', filename=filename)
