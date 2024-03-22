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
        # self.headers = {
        #     "Accept": "application/json",
        #     "xi-api-key": api_key,
        #     "Content-Type": "application/json"
        # }
        # self.url = "https://api.elevenlabs.io/v1/voices"
        # self.cloned_voices = self.fetch_cloned_voices()

    # def fetch_cloned_voices(self):
    #     response = requests.get(self.url, headers=self.headers)
    #     data = response.json()
    #     return [voice for voice in data["voices"] if voice["category"] == "cloned"]

    def verify_wav_file(self, file_stream):
        try:
            file_stream.seek(0)
            with wave.open(file_stream, 'rb') as wav_file:
                return True
        except wave.Error:
            return False

    async def process_audio(self, file: UploadFile):
        print("---- [process_audio] ----")
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
        print("---- [clone_voice] ----")

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

            print("voice에 뭐 찍히는지 확인 : ", voice)

            # # 클론이 완료되면 클론된 보이스 목록을 다시 가져옴
            # self.cloned_voices = self.fetch_cloned_voices()

            user_voice_id = voice.voice_id
            print("voice_id 확인 : ", user_voice_id)

            return user_voice_id

        # try:
        #     files_data = [('files', (file, open(file, 'rb'), 'application/octet-stream')) for file in files]
        #     print("files_data 확인 : ", files_data)
        #
        #     url = "https://api.elevenlabs.io/v1/voices/add"
        #
        #     payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n{user_id}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"files\"\r\n\r\n[\n  \"{files_data}\"\n]\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\n\"Read fairy tales in a friendly and cheerful way.\"\r\n-----011000010111000001101001--\r\n\r\n"
        #     headers = {
        #         "xi-api-key": self.api_key,
        #         "Content-Type": "multipart/form-data"
        #     }
        #
        #     response = requests.request("POST", url, data=payload, headers=headers)
        #
        #     print("clone_voice response 확인 : ", response)
        #     print("voice_id 확인 : ", response.text)
        #
        #     return response.text

        except Exception as e:
            print(f"An error occurred: {str(e)}")

            return None
