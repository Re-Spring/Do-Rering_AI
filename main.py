# 전체 동작할 로직 작성
import os, sys
import json

import uvicorn
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


# Module import
from routers.large_language_model_module import Large_language_model_module
from routers.voice_module import Voice_synthesizer
from routers.voice_cloning_module import Voice_cloning
from routers.dubbing_module import Dubbing_voice_cloning

# prompt key 값 가져오기
load_dotenv()
OPEN_API_KEY = os.environ.get("OPENAI_API_KEY")
VOICE_CLONING_API_KEY = os.environ.get("VOICE_CLONING_API_KEY")
client = OpenAI(api_key=OPEN_API_KEY)


# 기본 환경설정
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# 외부 접근 정채
# CORS 미들웨어를 사용하여 모든 외부 접근을 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 인스턴스 생성
llm_module = Large_language_model_module(api_key=OPEN_API_KEY)
ai_voice_module = Voice_synthesizer(api_key=OPEN_API_KEY)
voice_cloning_module = Voice_cloning(api_key=VOICE_CLONING_API_KEY)
clone_dubbing_module = Dubbing_voice_cloning(api_key=VOICE_CLONING_API_KEY)

# 필요한 엔드포인트
# 1. 동화 생성 엔드포인트 -> 이야기 생성 + 이미지 생성 + 더빙 + 앞에 내용을 기반으로 동영상으로 동화 생성
# 2. 목소리 voice_cloning 학습 엔드포인트


# 동화 생성 엔드포인트
# 매개 변수에 voice 추가
@app.post("/generateStory")
async def generate_story_endpoint(request: Request):
    print("aaa")
    # LLM_module의 generate_story 함수를 호출하여 응답을 story 변수에 저장
    story = await llm_module.generate_story(request)

    # story_response에서 JSON 데이터를 추출
    story_data = json.loads(story.body.decode('utf-8'))

    # 추출한 데이터를 바탕으로 필요한 처리를 수행
    # 예: 각 단락(paragraph)을 리스트로 변환
    # story_paragraphs = [value for key, value in story_data.items() if key.startswith("paragraph")]

    # 여기에 for문 넣어서 페이지별로 더빙 or voiceCloing -> 음성파일 생성
    page1 = story_data["paragraph1"]
    len_story = len(story_data)
    print(page1)
    print(len(story_data))

    # 여기 부분에 T2I 들어갈 예정

    # 더빙 부분에 if 문으로 사용 음성 종류에 따라 voice_cloning 파트와 dubbing 파트로 구분 예정

    # 여기부터 음성 파일
    # dubbing_module : 클로닝 데이터로 더빙

    # Dubbing 파트(일반 AI 목소리)
    # "echo" 부분의 voice 입력 받을 수 있도록 할 예정
    # if(voice != "myVoice"):
    #     for i in range(0, len_story):
    #         ai_voice_module.generate_audio_file("echo", story_data[f"paragraph{i}"])
    # else:
    #     clone_dubbing_module.generate_audio(page1, "user1")

    # 각 페이지 별 동화를 영상화 -> 페이지가 6개다. -> 영상 6개
    # audio + image + text -> page 별 영상 1~6p
    # 각 페이지 별 영상을 합침 -> 동화 완성

    return story
    # return await llm_module.generate_story(request)


# 목소리 voice_cloning 학습 엔드포인트
@app.post("/voiceCloning")
async def generate_voice_cloning_endpoint(request: Request):
    # voice_cloning_module : 학습
    return request

# 서버 자동 실행 ( 파이썬은 포트 8002 쓸거임)
if __name__ == "__main__":
    uvicorn.run("main:app", port=8002, reload=True)