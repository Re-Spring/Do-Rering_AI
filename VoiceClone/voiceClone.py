import wave
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi import FastAPI, File, Form, UploadFile
import tempfile
from starlette.requests import Request
from elevenlabs.client import ElevenLabs
import os
from elevenlabs import clone, generate, play
import soundfile as sf
import noisereduce as nr
import io
from pydub import AudioSegment
import numpy as np
import requests
import json

app = FastAPI()

# API_KEY = os.environ.get("ELEVEN_API_KEY")
API_KEY = "445ae443b70fb2f8d2f5e0e832419858"

# 실행 : uvicorn VoiceClone.voiceClone:app

@app.get('/', response_class=HTMLResponse)
async def index():
    with open("templates/voicecloning/cloneHome.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/recording", response_class=HTMLResponse)
async def get_regist_html(request: Request):
    with open("templates/voicecloning/recording.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/dubbing", response_class=HTMLResponse)
async def get_regist_html(request: Request):
    with open("templates/voicecloning/dubbing.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/process-audio")
async def process_audio(audio: UploadFile = File(...)):
    # 오디오 데이터 읽기
    audio_bytes = await audio.read()
    audio_stream = io.BytesIO(audio_bytes)
    
    # wav 파일인지 검증
    def verify_wav_file(file_stream):
        try:
            # WAV 파일 열기
            file_stream.seek(0)  # 스트림 포인터를 시작 위치로 리셋
            with wave.open(file_stream, 'rb') as wav_file:
                # 필요한 경우 파일의 속성들을 확인할 수 있음
                print("Channels:", wav_file.getnchannels())
                print("Sample width:", wav_file.getsampwidth())
                print("Frame rate (sample rate):", wav_file.getframerate())
                print("Number of frames:", wav_file.getnframes())
                print("Params:", wav_file.getparams())
                # 파일이 성공적으로 열렸으므로 유효한 WAV 파일임
                return True
        except wave.Error as e:
            # wave.Error 예외가 발생하면 파일이 유효하지 않은 WAV 형식임
            print(f"An error occurred: {e}")
            return False
    
    if not verify_wav_file(audio_stream):
        return HTMLResponse(status_code=400, content="제공된 파일이 유효한 WAV 형식이 아닙니다.")
    
    # 오디오 데이터 처리
    audio_stream.seek(0)  # 오디오 파일 처리를 위해 스트림 포인터 리셋
    with wave.open(audio_stream, 'rb') as wav_file:
        sample_rate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        channels = wav_file.getnchannels()
        sampwidth = wav_file.getsampwidth()
        audio_data = np.frombuffer(wav_file.readframes(n_frames), dtype=np.int16)
        
    # 오디오 데이터가 다중 채널일 경우 모노로 변환
    if channels > 1:
        audio_data = audio_data.reshape(-1, channels)
        audio_data = audio_data.mean(axis=1)
    
    # noisereduce 적용
    reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)
    
    # 잡음이 제거된 오디오를 임시 파일에 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        with wave.open(tmpfile.name, 'wb') as wave_output:
            wave_output.setnchannels(1)
            wave_output.setsampwidth(sampwidth)
            wave_output.setframerate(sample_rate)
            wave_output.writeframes(reduced_noise_audio.astype(np.int16).tobytes())
        
        return FileResponse(path=tmpfile.name, media_type='audio/wav')

@app.post('/save', response_class=HTMLResponse)
async def save_audio(request: Request, audio_data: bytes = File(...), user_id: str = Form(...)):
    try:
        # 받아온 사용자 ID를 파일명으로 지정하여 오디오 파일 저장
        audio_filename = f"static/voicecloning/user_voice_sample/{user_id}_recording.wav"
        with open(audio_filename, 'wb') as audio_file:
            audio_file.write(audio_data)
        
        # 저장 성공 메시지 반환
        return HTMLResponse(content=f"{user_id[-1]}번 녹음이 등록 완료!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return HTMLResponse(content="녹음 파일을 등록하는 중 오류가 발생했습니다. 불편을 드려 정말 죄송합니다. 다시 녹음을 시도해 주세요.")


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


@app.post('/clone')
async def clone_voice(request: Request):
    body = await request.json()  # 요청에서 JSON 본문 추출

    user_id = body.get('user_id')

    user_voice_id = next((voice["voice_id"] for voice in cloned_voices if voice["name"] == user_id), None)
    print(user_voice_id)

    try:
        # Voice clone 생성
        voice = clone(
            api_key=API_KEY,
            name=user_id,
            description="Read fairy tales in a friendly and cheerful way.",
            files=[f"static/voicecloning/user_voice_sample/{user_id}_1_recording.wav", f"static/voicecloning/user_voice_sample/{user_id}_2_recording.wav", f"static/voicecloning/user_voice_sample/{user_id}_3_recording.wav"],
        )
        return HTMLResponse(content="Voice Clone 완료! 이제 등록된 목소리로 동화를 더빙해 보세요!")
    except Exception as e:
        print (f"An error occurred: {str(e)}")
        return HTMLResponse(content="User ID가 제공되지 않았습니다.")

@app.post('/generate')
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

if __name__ == '__voiceClone__':
    uvicorn.run(app, host="127.0.0.1", port=8001)