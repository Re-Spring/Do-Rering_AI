# 모듈을 사용할 엔드포인트
import os, sys
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from openai import OpenAI
import json

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from routers.large_language_model_module import Large_language_model_module

# prompt key값
load_dotenv()
API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key = API_KEY)

# 기본 환경설정
app = FastAPI()
app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates/large_language_model")

# 인스턴스
llm_module = Large_language_model_module(api_key=API_KEY)

# dubbing = Dubbing_VoiceCloning(api_key=API_KEY)


# 엔드 포인트
@app.get("/")
def home(request : Request):
    return templates.TemplateResponse("LLM_test.html", {"request": request})

@app.post("/generate-story")
async def generate_story_endpoint(request: Request):
    # LLM_module의 generate_story 함수를 호출하여 응답을 story 변수에 저장
    story = await llm_module.generate_story(request)

    # story_response에서 JSON 데이터를 추출
    story_data = json.loads(story.body.decode('utf-8'))

    # 추출한 데이터를 바탕으로 필요한 처리를 수행
    # 예: 각 단락(paragraph)을 리스트로 변환
    # story_paragraphs = [value for key, value in story_data.items() if key.startswith("paragraph")]

    # 여기에 for문 넣어서 페이지별로 더빙 or voiceCloing -> 음성파일 생성
    page1 = story_data["paragraph1"]
    print(page1)

    return story
    # return await llm_module.generate_story(request)