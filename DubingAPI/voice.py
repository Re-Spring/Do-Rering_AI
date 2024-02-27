####### lib 설치 ##########
# pip install openai
# pip install streamlit
###########################
# 실행 : streamlit run voice.py
###########################
# 원하는 스크립트를 성우를 선택해서 읽도록 만들어줌
###########################

import os
import streamlit as st
from openai import OpenAI
import openai
from dotenv import load_dotenv
from datetime import datetime

# .env 파일 로드
load_dotenv()

API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY
)

st.title("OpenAI's Text-to-Audio Response")

# 인공지능 성우 선택 박스를 생성.
options = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
selected_option = st.selectbox("성우를 선택하세요:", options)

# 인공지능 성우에게 프롬프트 전달
default_text = '오늘은 생활의 꿀팁을 알아보겠습니다.'
user_prompt = st.text_area("인공지능 성우가 읽을 스크립트를 입력해주세요.", value=default_text, height=200)

# Generate Audio 버튼을 클릭하면 True가 되면서 if문 실행.
if st.button("Generate Audio"):
    # 텍스트로부터 음성을 생성.
    audio_response = client.audio.speech.create(
        model="tts-1",
        voice=selected_option,
        input=user_prompt,
    )

    # 현재 날짜와 시간을 이용하여 파일 이름 생성
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    audio_file_path = f"static/DubingAPI_audio/{current_datetime}.mp3"

    # 음성 파일을 저장.
    audio_content = audio_response.content
    with open(audio_file_path, "wb") as audio_file:
        audio_file.write(audio_content)

    # mp3 파일을 재생.
    st.audio(audio_file_path, format="audio/mp3")
