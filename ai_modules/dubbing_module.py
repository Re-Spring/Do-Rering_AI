# voice_cloning.py
from elevenlabs.client import ElevenLabs
import requests
# from elevenlabs import generate
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
        # return [voice for voice in data["voices"] if voice["category"] == "cloned"]
        return data["voices"]

    def generate_audio(self, title, story_text, user_id, num):
        print("---- [generate_audio] ----")
        # user_voice_id = next((voice["voice_id"] for voice in self.cloned_voices if voice["name"] == user_id), None)
        matching_voices = [voice for voice in self.cloned_voices if voice["category"] == "cloned" and voice["name"] == user_id]
        if matching_voices:
            user_voice_id = matching_voices[0]["voice_id"]
            print("[Dubbing_voice_cloning] generate_audio user_voice_id : ", user_voice_id)
        else:
            raise ValueError("Invalid user ID")
        output_filename = f"{self.audio_path}/{user_id}/{title}/{title}_{num + 1}Page.wav"
        output_path = Path(f"{self.audio_path}/{user_id}/{title}")

        if not output_path.exists():
            output_path.mkdir(parents=True)

        client = ElevenLabs(
            api_key=self.api_key
        )

        # 텍스트를 음성으로 변환(이터러블한 제너레이터 객체를 반환)
        audio = client.generate(
            text=story_text,
            voice=user_voice_id,
            model="eleven_multilingual_v2"
        )

        # audio 제너레이터가 생성하는 각 chunk를 순회하며, 이를 바이너리 모드로 열린 파일에 바이트 단위로 쓰기를 반복
        with open(output_filename, 'wb') as audio_file:
            for chunk in audio:
                audio_file.write(chunk)

        return output_filename
