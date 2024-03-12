import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
class Voice_synthesizer:
    def __init__(self, api_key, audio_path):
        self.api_key = api_key
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.audio_path = audio_path

    def generate_audio_file(self, voice: str, script: str, title: str, page, user_id):
        now = datetime.now()
        filename = f"{user_id}/{title}/{title}_{page}Page" + ".wav"
        audio_path = Path(os.path.join(self.audio_path, f"{user_id}/{title}"))
        audio_file_path = os.path.join(self.audio_path, filename)

        if not audio_path.exists():
            audio_path.mkdir(parents = True)
        
        audio_response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=script,
        )

        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(audio_response.content)

        return audio_file_path