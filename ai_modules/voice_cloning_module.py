import os
import tempfile
import wave
import numpy as np
import noisereduce as nr
import io
import requests
from elevenlabs.client import ElevenLabs
from fastapi import UploadFile

class Voice_cloning_module:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.url = "https://api.elevenlabs.io/v1/voices"
        self.cloned_voices = self.fetch_cloned_voices()

    def fetch_cloned_voices(self):
        response = requests.get(self.url, headers=self.headers)
        data = response.json()
        return [voice for voice in data["voices"] if voice["category"] == "cloned"]

    def verify_wav_file(self, file_stream):
        try:
            file_stream.seek(0)
            with wave.open(file_stream, 'rb') as wav_file:
                return True
        except wave.Error:
            return False

    async def process_audio(self, file: UploadFile):
        audio_bytes = await file.read()
        audio_stream = io.BytesIO(audio_bytes)

        if not self.verify_wav_file(audio_stream):
            return None, "Invalid WAV format"

        audio_stream.seek(0)

        with wave.open(audio_stream, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            channels = wav_file.getnchannels()
            sampwidth = wav_file.getsampwidth()
            audio_data = np.frombuffer(wav_file.readframes(n_frames), dtype=np.int16)

        if channels > 1:
            audio_data = audio_data.reshape(-1, channels).mean(axis=1)
            audio_data = audio_data.mean(axis=1)

        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)

        tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with wave.open(tmpfile, 'wb') as wave_output:
            wave_output.setnchannels(1)
            wave_output.setsampwidth(sampwidth)
            wave_output.setframerate(sample_rate)
            wave_output.writeframes(reduced_noise_audio.astype(np.int16).tobytes())
        tmpfile.close()

        return tmpfile.name, None

    async def clone_voice(self, user_id: str, files: list):
        # body = request.json()  # 요청에서 JSON 본문 추출
        # user_id = body.get('userId')

        client = ElevenLabs(
            api_key=self.api_key
        )

        try:
            # Voice clone 생성
            voice = client.clone(
                name=user_id,
                description="Read fairy tales in a friendly and cheerful way.",
                files=files,
            )

            user_voice_id = next((voice["voice_id"] for voice in self.cloned_voices if voice["name"] == user_id), None)
            print(user_voice_id)

            # 임시 파일들을 삭제합니다.
            for file in files:
                os.remove(file)

            return user_voice_id
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            # 임시 파일들을 삭제합니다.
            for file in files:
                os.remove(file)
            return None
