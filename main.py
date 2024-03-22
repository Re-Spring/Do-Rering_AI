# 전체 동작할 로직 작성
import asyncio
import os
import json
import time
from typing import List
import uvicorn
from openai import OpenAI
from fastapi import FastAPI, Request, BackgroundTasks, File, UploadFile, Form, Path
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.responses import JSONResponse

import config
# Module import
from config import STABILITY_KEY, image_path, image_font_path, DEEPL_API_KEY, audio_path, FIREBASE_SERVER_KEY

from ai_modules.large_language_model_module import Large_language_model_module
from ai_modules.voice_module import Voice_synthesizer
from ai_modules.voice_cloning_module import Voice_cloning_module
from ai_modules.dubbing_module import Dubbing_voice_cloning
from ai_modules.text_to_image import Text_to_image, T2I_generater_from_prompts
from ai_modules.deepl_ai import Deepl_api
from ai_modules.video_module import Video_module
from ai_modules.delete_voice_module import Delete_voice_module
from db.controller.story_controller import StoryController
from db.controller.clone_controller import CloneController
from pyfcm import FCMNotification
from pydantic import BaseModel


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
delete_module = Delete_voice_module(api_key=VOICE_CLONING_API_KEY)
story_controller = StoryController()
clone_controller = CloneController()

push_service = FCMNotification(api_key=config.FIREBASE_SERVER_KEY)
smile = "\U0001F601"

@app.post("/generateStory")
async def generate_story(request: Request):
    print("generate_story 들어옴")
    request_data = await request.json()
    story = await llm_module.generate_story(request)
    story_data = json.loads(story.body.decode('utf-8'))
    
    title = story_data["paragraph0"]
    voice = request_data["voice"]
    genre = request_data["genre"]
    user_id = request_data["userId"]
    user_code = request_data["userCode"]
    token = request_data["token"]
    print("token", token)

    len_story = len(story_data)
    print("len : ", len_story)
    korean_prompts = [story_data["paragraph" + str(i)] for i in range(len_story)]

    english_prompts = deepl_module.translate_text(text=korean_prompts, target_lang="EN-US")
    english_prompts = [english_prompts[i].text for i in range(0, len(english_prompts))]

    no_title_ko_pmt = []
    no_title_eng_pmt = []
    for i in range(1, len_story):
        no_title_ko_pmt.append(korean_prompts[i])
        no_title_eng_pmt.append(english_prompts[i])

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
            # AI 음성 모듈을 사용하여 음성 파일을 생성합니다.
            audio_file_path = ai_voice_module.generate_audio_file(voice, story_data[page], title,i, user_id=user_id)
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

    eng_title = english_prompts[0]

    title_image_paths = t2i_prompt_module.title_images_from_prompt(eng_title=eng_title, title=title, user_id=user_id)
    initial_seed=title_image_paths[1]

    main_image_paths = (t2i_prompt_module.story_images_from_prompts(
            no_title_ko_pmt=no_title_ko_pmt, no_title_eng_pmt=no_title_eng_pmt, title=title, user_id=user_id, initial_seed=initial_seed ))

    video_paths = []

    for i in range(0, len_story):
        audio_name = f"{user_id}/{title}/{title}_{i}Page.wav"
        print("audio_name : ", audio_name)
        print("get_audio_length 들어감")
        audio_len = video_module.get_audio_length(audio_name=audio_name)
        print("get_audio_length 나옴")
        print("audio_len : ", audio_len)
        if i == 0:
            print("title_image_paths : ", title_image_paths)
            video_path = video_module.generate_video(page=i, title=title, image_path=title_image_paths[2], audio_path=audio_paths[i], audio_length=audio_len)
        else:
            print("main_image_paths : ", main_image_paths[i-1])
            video_path = video_module.generate_video(page=i, title=title, image_path=main_image_paths[i-1], audio_path=audio_paths[i], audio_length=audio_len)
        video_paths.append(video_path)

    print("오디오 생성 완료")
    concatenate_video_path = video_module.concatenate_videos(video_paths=video_paths, title=title)

    story_summmary = await llm_module.summary_story(english_prompts=summary_prompts)
    story_summmary = json.loads(story_summmary.body.decode('utf-8'))


    fairytale_code = story_controller.insert_and_select_story_controller([user_code, story_summmary, title, genre, title_image_paths[2]])
    story_controller.insert_video_controller(fairytale_code, concatenate_video_path)


    result = push_service.notify_single_device(
        registration_id=token,
        message_title=f"요청하신 {title} 동화가 만들어졌어요!",
        message_body=f"즐거운 동화를 보러가봐요 {smile}"
    )

    print(f"finish generate {title}")
    return {"result": "Story generated successfully", "fcm_result": result}


# 목소리 voice_cloning 학습 엔드포인트
@app.post("/voiceCloning")
async def generate_voice_cloning_endpoint(user_id: str = Form(...), files: List[UploadFile] = File(...)):
    print("---- [generate_voice_cloning_endpoint] ----")

    # 업로드된 파일 처리
    saved_files = []
    for file in files:
        # await 키워드를 추가하여 비동기 함수의 결과를 기다림
        temp_file_name, error = await voice_cloning.process_audio(file)
        if error:
            print(f"An error occurred at process_audio : {str(error)}")
            return JSONResponse(status_code=400, content={"message": "An error occurred at process_audio"})
        saved_files.append(temp_file_name)

    # 파일들을 모두 처리한 후 clone_voice 호출
    user_voice_id = await voice_cloning.clone_voice(user_id, saved_files)
    if not user_voice_id:
        return JSONResponse(status_code=500, content={"message": "An error occurred at clone_voice"})

    update_success = clone_controller.update_voice_id_controller(user_id, user_voice_id)
    if not update_success:
        return JSONResponse(status_code=500, content={"message": "An error occurred at update_database"})

    return JSONResponse(status_code=200, content={"userVoiceId": user_voice_id})


# Pydantic 모델을 정의하여 요청 본문의 구조를 지정합니다.
# 이 모델은 클라이언트로부터 받은 데이터의 유효성 검사를 자동으로 수행해줍니다.
class VoiceIdRequest(BaseModel):
    voiceId: str    # 요청 본문에서 기대하는 'voiceId' 필드를 정의합니다.

# 'request_body' 변수는 클라이언트로부터 받은 요청 본문을 'VoiceIdRequest' 모델의 인스턴스로 변환하여 저장합니다.
@app.post("/deleteVoice")
async def delete_voice_id_endpoint(request_body: VoiceIdRequest):
    print("---- [delete_voice_id_endpoint] ----")
    voice_id = request_body.voiceId

    status = await delete_module.delete_voice(voice_id)
    if status.status_code == 200:
        delete_success = clone_controller.delete_voice_id_controller(voice_id)

        if not delete_success:
            return JSONResponse(status_code=500, content={"message": "An error occurred at update_database"})

        return JSONResponse(status_code=200, content={"message": "delete_voice_id_endpoint success"})

    else:
        return JSONResponse(status_code=500, content={"error": status.text})





# 서버 자동 실행 ( 파이썬은 포트 8002 쓸거임 )
if __name__ == "__main__":
    uvicorn.run("main:app", port=8002, reload=True)

