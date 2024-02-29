from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse
from elevenlabs.client import ElevenLabs

router = APIRouter()

# API_KEY = os.environ.get("ELEVEN_API_KEY")
API_KEY = "445ae443b70fb2f8d2f5e0e832419858"

# GET 요청을 보낼 API 엔드포인트의 URL입니다.
url = "https://api.elevenlabs.io/v1/voices"
# HTTP 요청에 대한 헤더가 설정됩니다.
# 헤더는 요청에 대한 메타데이터를 제공합니다. 이 경우, 내용 유형을 지정하고 인증을 위해 API 키를 포함하고 있습니다.
headers = {
"Accept": "application/json",
"xi-api-key": API_KEY,
"Content-Type": "application/json"
}
# URL과 헤더를 전달하여 API 엔드포인트에 GET 요청을 보냅니다.
response = requests.get(url, headers=headers)
# 'requests' 라이브러리의 내장 .json() 메소드를 사용하여 API로부터의 JSON 응답을 파싱합니다.
# 이는 JSON 데이터를 추가 처리를 위한 파이썬 딕셔너리로 변환합니다.
data = response.json()
# 'category'가 'cloned'인 요소만 추출
cloned_voices = [voice for voice in data["voices"] if voice["category"] == "cloned"]

@router.post('/generate')
async def generate_audio(request: Request):
    # 클라이언트로부터 텍스트 데이터 받기
    data = await request.json()
    story_text = data.get('storyText', '')
    user_id = data.get('userId', '')
    user_voice_id = next((voice["voice_id"] for voice in cloned_voices if voice["name"] == user_id), None)

    if user_voice_id is None:
        # 사용자 ID가 잘못되었을 경우 오류 메시지 반환
        raise HTTPException(status_code=400)

    # 텍스트를 음성으로 변환
    audio = generate(
        api_key=API_KEY,
        text=story_text,
        voice=user_voice_id,
        model="eleven_multilingual_v2"
    )
    
    # 생성된 오디오 파일 저장
    output_filename = f"static/voicecloning/user_dubbing/{user_id}_generated_audio.wav"
    with open(output_filename, 'wb') as audio_file:
        audio_file.write(audio)

    # 저장된 파일을 클라이언트에게 반환
    return FileResponse(output_filename, filename=output_filename)