from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import openai

app = FastAPI()

# OpenAI 클라이언트 초기화
openai.api_key = "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"

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    # T2I/dalle.html 템플릿을 렌더링하여 반환
    return templates.TemplateResponse("T2I/dalle.html", {"request": request})

@app.post("/generate-image", response_class=HTMLResponse)
async def generate_image(request: Request, prompt: str = Form(...)):
    # OpenAI API를 호출하여 이미지 생성
    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response['data'][0]['url']
    
    # 생성된 이미지 URL을 템플릿에 포함시켜 반환
    return templates.TemplateResponse("image_display.html", {"request": request, "image_url": image_url})
