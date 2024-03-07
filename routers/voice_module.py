import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

class Voice_synthesizer:
    def __init__(self, api_key):
        self.api_key = api_key
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.audio_files_directory = "static/dubing/audios"
        os.makedirs(self.audio_files_directory, exist_ok=True)

    def generate_audio_file(self, voice: str, script: str, title: str, page):
        now = datetime.now()
        filename = title + f"_{page}Page" + ".mp3"
        audio_file_path = os.path.join(self.audio_files_directory, filename)
        
        audio_response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=script,
        )

        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(audio_response.content)

        return filename, f"/download-audio/{filename}"