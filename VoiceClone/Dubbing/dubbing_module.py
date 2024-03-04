# voice_cloning.py
from elevenlabs.client import ElevenLabs
import requests
from elevenlabs import generate

class VoiceCloning:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.elevenlabs.io/v1/voices"
        self.headers = {
            "Accept": "application/json",
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        self.cloned_voices = self.fetch_cloned_voices()

    def fetch_cloned_voices(self):
        response = requests.get(self.url, headers=self.headers)
        data = response.json()
        return [voice for voice in data["voices"] if voice["category"] == "cloned"]

    def generate_audio(self, story_text, user_id):
        user_voice_id = next((voice["voice_id"] for voice in self.cloned_voices if voice["name"] == user_id), None)
        if user_voice_id is None:
            raise ValueError("Invalid user ID")

        # 텍스트를 음성으로 변환
        audio = generate(
            api_key=self.api_key,
            text=story_text,
            voice=user_voice_id,
            model="eleven_multilingual_v2"
        )
    
        # 생성된 오디오 파일 저장
        output_filename = f"../../static/voicecloning/user_dubbing/{user_id}_generated_audio.wav"
        with open(output_filename, 'wb') as audio_file:
            audio_file.write(audio)

        return audio, user_voice_id, output_filename
