from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from openai import OpenAI
from PIL import Image
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import io
import base64
from fastapi.staticfiles import StaticFiles
import httpx
from fastapi.middleware.cors import CORSMiddleware
# from typing import List
from typing import Dict
from pydantic import BaseModel

load_dotenv()

API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key = API_KEY
)

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시 특정 도메인으로 제한하는 것이 좋습니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates/LLM")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 이미지 프롬프트 리스트를 받는 스키마 정의
# class ImagePrompt(BaseModel):
#     prompts: List[str] # 여러 프롬프트를 리스트로 받음

class ImagePrompt(BaseModel):
    prompts: Dict[str, str]  # 키와 값 모두 문자열인 딕셔너리

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("LLM_test.html", {"request": request})

@app.post("/mkimg")
async def get_images(prompt: ImagePrompt):
    print("get_image 들어옴")
    image_paths = []

    # 각 프롬프트에 대해 이미지 생성 및 경로 저장
    for i, prompt_text in enumerate(prompt.prompts):
        response = client.images.generate(
            model="dall-e-3",
            # 이미지 생성 prompt가 더 이미지를 잘 생성하도록 만들기static/LLM
            prompt=prompt_text+"라는 내용의 동화 페이지의 장면에 어울리는 그림을 동화 그림체로 만들어줘",
            size="1024x1024",
            quality="standard",
            response_format='b64_json',
            n=1,
        )
        image_data = base64.b64decode(response.data[0].b64_json)
        print("image_data : ", image_data)
        image = Image.open(io.BytesIO(image_data))
        print("image : ", image)
        image_path = f'static/LLM/images/output_{i}.png'
        print("image_path : ", image_path)
        image.save(image_path)
        image_paths.append(image_path)

    return JSONResponse({'image_paths': image_paths})




# 여긴 스토리 창작 엔드포인트
@app.post("/generate-story")
async def generate_stoy(request: Request):
    # 클라이언트로부터 전송받은 JSON 데이터를 파싱합니다.
    data = await request.json()

    keys_to_delete = []  # 삭제할 키를 저장할 빈 리스트 생성

    for key, value in data.items():  # data.items()로 키-값 쌍들을 반복
        if value == "":  # 값이 빈 문자열인 경우
            keys_to_delete.append(key)  # 삭제할 키를 리스트에 추가

    for key in keys_to_delete:  # 삭제할 키들을 반복하면서
        del data[key]  # 딕셔너리에서 해당 키-값 쌍을 제거

    title = data.get("title", "no request data")
    character = data.get("character", "no request data")
    # subject = data.get("subject", "no request data")
    genre = data.get("genre", "no request data")
    keyword = data.get("keyword", "no request data")
    lesson = data.get("lesson", "no request data")
    page = data.get("page", "no request data")
    # story = data.get("story", "no requst data")

    api_key = API_KEY

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 이 프롬프트는 동화 생성에 사용됩니다. 필요에 따라 수정 가능합니다.
    payload = {
        # option : gpt - streaming
        "model": "gpt-4-turbo-preview",  # 또는 최신 GPT 모델을 사용하세요.
        # "prompt" :
        "messages": [
        # role : user = 유저가 할 질문
        # role : system = GPT의 역할 [ex)너는 동화 작가야] 
        {
            
            "role": "system", "content":f"""
    # Role
    You are a fairy tale writer who creates fairy tales professionally and creatively.

    # Audience
    - This is for Python developers who want to develop an automatic fairy tale generator.
    - Do not write any content other than the json string, because the resulting json string must be used directly in the script.

    # Task
    The ultimate goal is to generate fairy tales by referring to the data sent by the user.
    To do that, I'll think about each step.

    ## Step 1
    Set the settings for the fairy tale you receive by default.
    The title of the fairy tale: {title},
    The main character of the fairy tale: {character},
    Genre of fairy tales: {genre},
    Keyword of fairy tale: {keyword},
    Lessons from fairy tales: {lesson},
    Number of paragraphs in fairy tale: {page}

    If even one of the above setting values comes up with a value of no request data, go to Step 2,
    Or move on to Step 3.

    ## Step 2
    Displays only the remaining elements except for settings with no request data.

    ## Step 3
    If you go directly from Step 1, you can set the fairy tale setting in Step 1,
    If you have passed Step 2 instead of the above case, you should set the settings in Step 2
    Create a fairy tale using

    # policy
    - Please fill out the document type in the Json Format form below.
    - Do not write any content other than the json string, because the resulting json string must be used directly in the script.
    - Do not write unnecessary explanations or instructions.""",
            "role": "user", "content": f"동화를 생성해줘"
            } 
        ],
        "max_tokens": 3000,  # 필요에 따라 토큰 수 조정
        "temperature": 1,  # 창의성 정도 조정 0.7 ~ 1
        "n": 1,  # 생성할 완료 항목 수
    }

    timeout = httpx.Timeout(600.0, connect=600.0) 
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post('https://api.openai.com/v1/chat/completions', json=payload, headers=headers)
        
        # 상태 코드가 200이 아닐 경우
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        result = response.json()
        # print(result)
        # if 'choices' in result and 'text' in result['choices']:
        #     story_text = result['choices']['text'].strip()
        # else:
        #     print("응답 구조에서 'text' 정보를 찾을 수 없습니다.")

        # 'choices' 배열에서 첫 번째 항목을 가져옵니다.
        choice = result['choices'][0]  # 첫 번째 선택지를 가져옵니다.
        # print(result)
        # 'message' 객체 내의 'content' 필드에서 생성된 텍스트를 추출합니다.
        if 'message' in choice and 'content' in choice['message']:
            story_text = choice['message']['content'].strip()
            # print("story_text : " + story_text)  # 생성된 텍스트 출력
        else:
            print("응답 구조에서 'content' 정보를 찾을 수 없습니다.")
        # story_text = result['choices'][0]['text'].strip()
        story_text = choice['message']['content'].replace("제목:","").strip()
        paragraphs = story_text.split("\n\n")
        story_dict = {f"paragraphs{i}": para for i, para in enumerate(paragraphs)}
        print(story_dict)
        return JSONResponse(content=story_dict)