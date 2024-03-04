import tempfile
import wave
import numpy as np
import noisereduce as nr
import io
import requests

class VoiceCloning:
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

    def verify_wav_file(self, audio_bytes):
        try:
            audio_stream = io.BytesIO(audio_bytes)
            audio_stream.seek(0)
            with wave.open(audio_stream, 'rb') as wav_file:
                return True
        except wave.Error:
            return False

    def process_audio(self, audio_bytes):
        if not self.verify_wav_file(audio_bytes):
            return None, "Invalid WAV format"

        audio_stream = io.BytesIO(audio_bytes)
        audio_stream.seek(0)
        with wave.open(audio_stream, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            audio_data = np.frombuffer(wav_file.readframes(wav_file.getnframes()), dtype=np.int16)

        if wav_file.getnchannels() > 1:
            audio_data = audio_data.reshape((-1, wav_file.getnchannels())).mean(axis=1)

        reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            with wave.open(tmpfile, 'wb') as wave_output:
                wave_output.setnchannels(1)
                wave_output.setsampwidth(wav_file.getsampwidth())
                wave_output.setframerate(sample_rate)
                wave_output.writeframes(reduced_noise_audio.astype(np.int16).tobytes())

            return tmpfile.name, None
