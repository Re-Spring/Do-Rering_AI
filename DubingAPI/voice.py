import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

app = FastAPI()

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

templates = Jinja2Templates(directory="templates/Dubing")

AUDIO_FILES_DIRECTORY = "static/DubingVoice/audio_files"
os.makedirs(AUDIO_FILES_DIRECTORY, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dubing.html", {"request": request})

@app.post("/generate-audio/")
async def generate_audio(request: Request, voice: str = Form(...), script: str = Form(...)):
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M") + ".mp3"
    audio_file_path = os.path.join(AUDIO_FILES_DIRECTORY, filename)

    audio_response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=script,
    )

    with open(audio_file_path, "wb") as audio_file:
        audio_file.write(audio_response.content)
    
    # 음성 파일의 URL 반환
    return {"filename": filename, "audio_url": f"/download-audio/{filename}"}

@app.get("/download-audio/{filename}")
async def download_audio(filename: str):
    audio_file_path = os.path.join(AUDIO_FILES_DIRECTORY, filename)
    return FileResponse(path=audio_file_path, media_type='audio/mp3', filename=filename)
