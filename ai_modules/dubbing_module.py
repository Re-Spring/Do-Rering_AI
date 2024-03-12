# voice_cloning.py
from elevenlabs.client import ElevenLabs
import requests
from elevenlabs import generate
from pathlib import Path

class Dubbing_voice_cloning:
    def __init__(self, api_key, audio_path):
        self.api_key = api_key
        self.url = "https://api.elevenlabs.io/v1/voices"
        self.headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.audio_path = audio_path
        self.cloned_voices = self.fetch_cloned_voices()

    def fetch_cloned_voices(self):
        response = requests.get(self.url, headers=self.headers)
        data = response.json()
        return [voice for voice in data["voices"] if voice["category"] == "cloned"]

    def generate_audio(self, title, story_text, user_id, num):
        user_voice_id = next((voice["voice_id"] for voice in self.cloned_voices if voice["name"] == user_id), None)
        if user_voice_id is None:
            raise ValueError("Invalid user ID")
        output_filename = f"{self.audio_path}/{user_id}/{title}/{title}_{num + 1}Page.wav"
        output_path = Path(f"{self.audio_path}/{user_id}/{title}")

        if not output_path.exists():
            output_path.mkdir(parents=True)

        # 텍스트를 음성으로 변환
        audio = generate(
            api_key=self.api_key,
            text=story_text,
            voice=user_voice_id,
            model="eleven_multilingual_v2"
        )

        with open(output_filename, 'wb') as audio_file:
            audio_file.write(audio)

        return output_filename
