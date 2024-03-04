from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from voiceCloning_module import VoiceCloning

app = FastAPI()
voice_cloning = VoiceCloning(api_key="445ae443b70fb2f8d2f5e0e832419858")

@app.post("/process-audio")
async def process_audio(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    processed_audio_path, error = voice_cloning.process_audio(audio_bytes)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return FileResponse(processed_audio_path, media_type='audio/wav')

@app.post('/save')
async def save_audio(audio_data: bytes = File(...), user_id: str = Form(...)):
    try:
        audio_filename = f"./static/voicecloning/user_voice_sample/{user_id}_recording.wav"
        with open(audio_filename, 'wb') as audio_file:
            audio_file.write(audio_data)
        return HTMLResponse(content=f"Recording for user {user_id} saved successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# The `/clone` endpoint logic should be adapted based on how you intend to implement the cloning functionality with ElevenLabs API.
