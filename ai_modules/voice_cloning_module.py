import os
import tempfile
import wave

import httpx
import numpy as np
import noisereduce as nr
import io
from elevenlabs.client import ElevenLabs, AsyncElevenLabs
from fastapi import UploadFile


class Voice_cloning_module:
    def __init__(self, api_key):
        self.api_key = api_key

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

            user_voice_id = voice.voice_id

            return user_voice_id

        except Exception as e:
            print(e)
            return None
