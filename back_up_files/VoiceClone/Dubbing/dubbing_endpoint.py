# main.py
from fastapi import FastAPI, Request, HTTPException
from routers.dubbing_module import VoiceCloning
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
voice_cloning = VoiceCloning(api_key="445ae443b70fb2f8d2f5e0e832419858")
templates = Jinja2Templates(directory="../../templates/voice_cloning")

@app.get('/')
async def index(request : Request):
    return templates.TemplateResponse("dubbing.html", {"request": request})


# 이거 그대로 땡겨서 LLM_endpoint.py로 보내면 될듯
@app.post('/generate')
async def generate_audio_endpoint(request: Request):
    data = await request.json()
    story_text = data.get('storyText', '')
    user_id = data.get('userId', '')

    try:
        audio, user_voice_id,output_filename = voice_cloning.generate_audio(story_text, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

    return FileResponse(output_filename, filename=output_filename)
