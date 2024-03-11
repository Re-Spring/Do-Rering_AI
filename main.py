# 전체 동작할 로직 작성
import os
import json
import sys
import uuid

import uvicorn
from openai import OpenAI
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


# Module import
from config import STABILITY_KEY, image_path, image_font_path, DEEPL_API_KEY, audio_path

from routers.large_language_model_module import Large_language_model_module
from routers.voice_module import Voice_synthesizer
from routers.voice_cloning_module import Voice_cloning
from routers.dubbing_module import Dubbing_voice_cloning
from routers.text_to_image import Text_to_image, T2I_generater_from_prompts
from routers.deepl_ai import Deepl_api
from routers.video_module import generate_video_with_images_and_text


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
voice_cloning_module = Voice_cloning(api_key=VOICE_CLONING_API_KEY)
clone_dubbing_module = Dubbing_voice_cloning(api_key=VOICE_CLONING_API_KEY, audio_path=audio_path)
t2i_module = Text_to_image(api_key=STABILITY_KEY, image_font_path=image_font_path, image_path=image_path)
t2i_prompt_module = T2I_generater_from_prompts(api_key=STABILITY_KEY, image_font_path=image_font_path, image_path=image_path)
deepl_module = Deepl_api(api_key=DEEPL_API_KEY)


# 필요한 엔드포인트
# 1. 동화 생성 엔드포인트 -> 이야기 생성 + 이미지 생성 + 더빙 + 앞에 내용을 기반으로 동영상으로 동화 생성
# 2. 목소리 voice_cloning 학습 엔드포인트


# 동화 생성 엔드포인트
# 매개 변수에 voice 추가
@app.post("/generateStory")
async def generate_story_endpoint(request: Request):
    # 요청이 들어왔을 때의 로그를 출력합니다.
    print("엔드포인트 들어옴")
    # LLM_module의 generate_story 함수를 호출하여 응답을 story 변수에 저장
    story = await llm_module.generate_story(request)

    # 요청 데이터를 JSON 형식으로 변환합니다.
    request_data = await request.json()
    print("요청 데이터 : ", request_data)

    # 생성된 이야기를 JSON 형식에서 파싱합니다.
    print("스토리 완성")
    # story_response에서 JSON 데이터를 추출
    story_data = json.loads(story.body.decode('utf-8'))

    # 첫 번째 단락을 가져옵니다.
    title = story_data["paragraph0"]
    page1 = story_data["paragraph1"]

    # 이야기 데이터의 총 길이(단락 수)를 계산합니다.
    len_story = len(story_data)
    print(page1)
    print(len(story_data))

    # 첫 번째 단락과 전체 길이를 로그로 출력합니다.
    # print(page1)
    # print(len(story_data))

    # 한국어로 된 모든 단락을 리스트로 생성합니다.
    korean_prompts = [story_data["paragraph" + str(i)] for i in range(len_story)]
    print("korean_prompts", korean_prompts)

    # Deepl 모듈을 사용하여 한국어 단락을 영어로 번역합니다.
    english_prompts = deepl_module.translate_text(text=korean_prompts, target_lang="EN-US")

    # 번역된 결과에서 텍스트만 추출하여 리스트로 저장합니다.
    english_prompts = [english_prompts[i].text for i in range(len(english_prompts))]
    print("english_prompts", english_prompts)

    # 영어로 번역된 단락들을 이미지로 변환하는 모듈을 호출합니다.
    # t2i_prompt_module.generate_images_from_prompts(english_prompts=english_prompts, korean_prompts=korean_prompts)
    main_image_paths = (
        t2i_prompt_module.generate_images_from_prompts(
            english_prompts=english_prompts, korean_prompts=korean_prompts, title = title)
    )
    print("main_image_paths : ", main_image_paths)

    # Dubbing 파트(voiceCloning/dubbing)
    # "echo" 부분의 voice 입력 받을 수 있도록 할 예정
    # 요청 데이터에서 'voice' 파라미터를 추출합니다.
    voice = request_data["voice"]

    # 이야기의 제목을 추출합니다.
    title = story_data["paragraph0"]
    # 오디오 파일 생성 및 경로 저장
    audio_paths = []
    # 사용자가 설정한 목소리가 'myVoice'가 아닌 경우, AI가 제공하는 목소리로 음성 파일을 생성합니다.
    for i, page in enumerate(korean_prompts):
        # AI 음성 모듈이나 사용자 목소리 복제 모듈을 사용하여 오디오 파일 생성
        # 이 예제에서는 ai_voice_module.generate_audio_file 함수의 반환값이 오디오 파일 경로라고 가정
        audio_file_path = ai_voice_module.generate_audio_file(voice, page, title, i)
        audio_paths.append(audio_file_path)

    # 오디오 파일 중 하나를 비디오에 사용할 오디오로 선택
    print("audio_paths : ", audio_paths)
    selected_audio_path = audio_paths \
        if audio_paths else None
    print("selected_audio_path : ", selected_audio_path)

    # 최종 비디오 파일 경로 설정
    output_video_dir = os.path.join("", "videos")
    os.makedirs(output_video_dir, exist_ok=True)
    output_video_path = os.path.join(output_video_dir, f"{uuid.uuid4()}.wav")  # 고유한 파일명을 위해 uuid 사용

    # 이미지와 오디오 데이터를 사용해 비디오 생성
    if selected_audio_path:
        generate_video_with_images_and_text(
            image_paths=main_image_paths,
            audio_path=selected_audio_path,
            output_video_path=output_video_path,
            fps=24
        )

    # 비디오 생성 결과 반환 (예: URL 반환)
    video_url = f"/movies/{os.path.basename(output_video_path)}"
    return {"video_url": video_url}

    # if (voice != "myVoice"):
    #     for i in range(0, len_story):
    #         # 음성 파일 생성 중임을 로그로 출력합니다.
    #         print(f"페이지 {i + 1}번째 음성파일 생성중")
    #
    #         # 현재 페이지를 지정합니다.
    #         page = f"paragraph{i}"
    #
    #         # AI 음성 모듈을 사용하여 음성 파일을 생성합니다.
    #         ai_voice_module.generate_audio_file(voice, story_data[page], title, i + 1)
    # else:
    #     # 'myVoice'가 선택된 경우, 사용자의 목소리로 음성을 복제하여 음성 파일을 생성합니다.
    #     for i in range(0, len_story):
    #         # 음성 파일 생성 중임을 로그로 출력합니다.
    #         print(f"페이지 {i + 1}번째 음성파일 생성중")
    #
    #         # 현재 페이지를 지정합니다.
    #         page = f"paragraph{i}"
    #
    #         # 사용자의 목소리로 음성을 복제하는 모듈을 호출합니다.
    #         clone_dubbing_module.generate_audio(title, story_data[page], "hj1234", i)
    #
    # # 각 페이지 별 동화를 영상화 -> 페이지가 6개다. -> 영상 6개
    # # audios + image + text -> page 별 영상 1~6p
    # # 각 페이지 별 영상을 합침 -> 동화 완성
    #
    # return story
    # return await llm_module.generate_story(request)

# 목소리 voice_cloning 학습 엔드포인트
@app.post("/voiceCloning")
async def generate_voice_cloning_endpoint(request: Request):
    print("voiceCloning ENDpoint 들어옴")
    # voice_cloning_module : 학습
    return request

# 서버 자동 실행 ( 파이썬은 포트 8002 쓸거임 )
if __name__ == "__main__":
    uvicorn.run("main:app", port=8002, reload=True)