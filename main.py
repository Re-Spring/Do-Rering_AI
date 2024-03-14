# 전체 동작할 로직 작성
import asyncio
import os
import json

import uvicorn
from openai import OpenAI

from fastapi import FastAPI, Request, BackgroundTasks, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.websockets import WebSocket, WebSocketDisconnect
import asyncio

from starlette.responses import JSONResponse


import config
# Module import
from config import STABILITY_KEY, image_path, image_font_path, DEEPL_API_KEY, audio_path

from ai_modules.large_language_model_module import Large_language_model_module
from ai_modules.voice_module import Voice_synthesizer
from ai_modules.voice_cloning_module import Voice_cloning_module
from ai_modules.dubbing_module import Dubbing_voice_cloning
from ai_modules.text_to_image import Text_to_image, T2I_generater_from_prompts
from ai_modules.deepl_ai import Deepl_api
from ai_modules.video_module import Video_module
from db.controller.story_controller import StoryController


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
ai_voice_module = Voice_synthesizer(api_key=OPEN_API_KEY, audio_path=audio_path)
voice_cloning = Voice_cloning_module(api_key=VOICE_CLONING_API_KEY)
clone_dubbing_module = Dubbing_voice_cloning(api_key=VOICE_CLONING_API_KEY, audio_path=audio_path)
t2i_module = Text_to_image(api_key=STABILITY_KEY, image_font_path=image_font_path, image_path=image_path)
t2i_prompt_module = T2I_generater_from_prompts(api_key=STABILITY_KEY, image_font_path=image_font_path, image_path=image_path)
deepl_module = Deepl_api(api_key=DEEPL_API_KEY)
video_module = Video_module(video_path=config.video_path, audio_path=config.audio_path)
story_controller = StoryController()

connected_websockets = []

async def generate_story(data: json):
    # 요청이 들어왔을 때의 로그를 출력합니다.

  

    print("generate_story 들어옴")

    # LLM_module의 generate_story 함수를 호출하여 응답을 story 변수에 저장
    story = await llm_module.generate_story(data)

    # 요청 데이터를 JSON 형식으로 변환합니다.
    # story_response에서 JSON 데이터를 추출
    # 생성된 이야기를 JSON 형식에서 파싱합니다.


    story_data = json.loads(story.body.decode('utf-8'))

    title = story_data["paragraph0"]
    voice = data["voice"]
    genre = data["genre"]
    user_id = data["userId"]
    user_code = data["userCode"]

    # 이야기 데이터의 총 길이(단락 수)를 계산합니다.
    len_story = len(story_data)
    print("len : ", len_story)
    # 한국어로 된 모든 단락을 리스트로 생성합니다.

    korean_prompts = [story_data["paragraph" + str(i)] for i in range(len_story)]

    


    # Deepl 모듈을 사용하여 한국어 단락을 영어로 번역합니다.
    english_prompts = deepl_module.translate_text(text=korean_prompts, target_lang="EN-US")
    # 번역된 결과에서 텍스트만 추출하여 리스트로 저장합니다.
    english_prompts = [english_prompts[i].text for i in range(0, len(english_prompts))]

    summary_prompts = ""
    for i in range(1, 3):
        summary_prompts += english_prompts[i]


    audio_paths = []
    print("main_image 끝")
    # 사용자가 설정한 목소리가 'myVoice'가 아닌 경우, AI가 제공하는 목소리로 음성 파일을 생성합니다.
    if (voice != "myVoice"):
        for i in range(0, len_story):
            # 음성 파일 생성 중임을 로그로 출력합니다.
            print(f"페이지 {i + 1}번째 음성파일 생성중")
            # 현재 페이지를 지정합니다.
            page = f"paragraph{i}"
            user_id = f"hj1234"
            # AI 음성 모듈을 사용하여 음성 파일을 생성합니다.
            audio_file_path = ai_voice_module.generate_audio_file(voice, story_data[page], title, i + 1, user_id=user_id)
            audio_paths.append(audio_file_path)
    else:
        # 'myVoice'가 선택된 경우, 사용자의 목소리로 음성을 복제하여 음성 파일을 생성합니다.
        for i in range(0, len_story):
            # 음성 파일 생성 중임을 로그로 출력합니다.
            print(f"페이지 {i + 1}번째 음성파일 생성중")
            # 현재 페이지를 지정합니다.
            page = f"paragraph{i}"
            # 사용자의 목소리로 음성을 복제하는 모듈을 호출합니다.
            audio_file_path = clone_dubbing_module.generate_audio(title, story_data[page], user_id=user_id, num=i)
            audio_paths.append(audio_file_path)

    print("voice 끝")

    # 영어로 번역된 단락들을 이미지로 변환하는 모듈을 호출합니다.
    # t2i_prompt_module.generate_images_from_prompts(english_prompts=english_prompts, korean_prompts=korean_prompts, title=title)

    eng_title = english_prompts.pop(0)
    kor_title = korean_prompts.pop(0)

    print(f"영어 제목[0]번 인덱스 : {eng_title}")
    eng_image_paths = t2i_prompt_module.title_images_from_prompt(eng_title = eng_title, title=title, user_id=user_id)

    main_image_paths = (
        t2i_prompt_module.story_images_from_prompts(
            english_prompts=english_prompts, korean_prompts=korean_prompts, title=title, user_id=user_id)
    )

    video_paths = []

    for i in range(0, len_story):
        audio_name = f"{user_id}/{title}/{title}_{i+1}Page.wav"
        print("audio_name : ", audio_name)
        print("get_audio_length 들어감")
        audio_len = video_module.get_audio_length(audio_name=audio_name)
        print("get_audio_length 나옴")
        print("audio_len : ", audio_len)
        video_path = video_module.generate_video(page=i+1, title=title, image_path=main_image_paths[i], audio_path=audio_paths[i], audio_length=audio_len)
        video_paths.append(video_path)

    print("오디오 생성 완료")
    video_module.concatenate_videos(video_paths=video_paths, title=title)

    story_summmary = await llm_module.summary_story(english_prompts=summary_prompts)
    story_summmary = json.loads(story_summmary.body.decode('utf-8'))
    print("story_summary : ", story_summmary)
    data = [user_code, story_summmary, title, genre, main_image_paths[0]]

    print("생성 완료")
    story_controller.insert_story_controller(data)
    print("insert까지 끝")

    return {"message" : "즐거운 동화 생성을 시작했어요~ 완료되면 알려드릴게요!"}


# 목소리 voice_cloning 학습 엔드포인트
@app.post("/voiceCloning")
async def generate_voice_cloning_endpoint(request: Request):
    print("voiceCloning ENDpoint 들어옴")

    form = await request.json()
    user_id = form.get('userId')
    files = form.getlist('files')

    # 업로드된 파일 처리
    saved_files = []
    for file in files:
        content = await file.read()
        temp_file_name, error = voice_cloning.process_audio(content)
        if error:
            print(f"An error occurred at process_audio : {str(error)}")
            return JSONResponse(status_code=400, content={"message": error})
        saved_files.append(temp_file_name)

    # 파일들을 모두 처리한 후 clone_voice 호출
    user_voice_id = voice_cloning.clone_voice(user_id, saved_files)
    if not user_voice_id:
        return JSONResponse(status_code=500, content={"message": "오류가 발생했습니다"})

    return JSONResponse(status_code=200, content={"userVoiceId": user_voice_id})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, background_task: BackgroundTasks):
    print("web 소켓 뚫음")
    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            print("message : ", message)
            data = json.loads(message)
            if data:
                asyncio.create_task(generate_story(data))
    except WebSocketDisconnect:
        print("WebSocket connection disconnected")
        connected_websockets.remove(websocket)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


# 서버 자동 실행 ( 파이썬은 포트 8002 쓸거임 )
if __name__ == "__main__":
    uvicorn.run("main:app", port=8002, reload=True)

