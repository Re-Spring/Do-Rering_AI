import cv2
import os
import io
import uuid
import stability_sdk.client as stability_client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image
import numpy as np
import librosa
from moviepy.editor import VideoFileClip
from moviepy.editor import AudioFileClip
import pygame

stability_key = "sk-9IYJj4wxgqFs3J3zdZmGrf104OmiZMx4f8meFvfRF8Nw4hNM"

def load_audio(audio_file):
    """
    Load audio file using librosa.

    Parameters:
        audio_file (str): Path to the audio file.

    Returns:
        np.ndarray: Loaded audio data.
        int: Sampling rate of the audio file.
    """
    audio_data, sr = librosa.load(audio_file, sr=None)
    return audio_data, sr

def get_audio_duration(audio_file):
    """
    Get duration of audio file.

    Parameters:
        audio_file (str): Path to the audio file.

    Returns:
        float: Duration of the audio file in seconds.
    """
    audio_data, sr = load_audio(audio_file)
    duration = len(audio_data) / sr
    return duration

def play_audio(audio_folder):
    """
    Play audio files in the specified folder.

    Parameters:
        audio_folder (str): Path to the folder containing audio files.
    """
    # pygame 초기화
    pygame.mixer.init()

    # audio_folder 내의 모든 mp3 및 wav 파일을 재생합니다.
    for file_name in os.listdir(audio_folder):
        if file_name.endswith('.mp3') or file_name.endswith('.wav'):
            file_path = os.path.join(audio_folder, file_name)
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

def generate_video_with_images_and_text(story_text, audio_folder, image_folder, output_video_path, fps=1, frame_interval=1):
    # 이미지 저장 폴더 생성
    os.makedirs(image_folder, exist_ok=True)

    # API 설정
    stability_key = os.getenv('STABILITY_KEY')
    if stability_key is None:
        stability_key = input("The 'STABILITY_KEY' environment variable is not set. Please enter your STABILITY_KEY: ")
    stability_api = stability_client.StabilityInference(key=stability_key, verbose=True, engine="stable-diffusion-xl-1024-v1-0")

    # 문장마다 이미지 생성하고 저장
    sentences = story_text.strip().split('\n\n')
    audio_duration = sum(get_audio_duration(os.path.join(audio_folder, f)) for f in os.listdir(audio_folder) if f.endswith('.mp3') or f.endswith('.wav'))

    for i, sentence in enumerate(sentences):
        # 문장의 길이를 기반으로 이미지 수 계산
        sentence_duration = audio_duration / len(sentences)
        num_images = int(sentence_duration * fps)

        # 동적으로 seed 값 설정 (무작위성 증가)
        seed = np.random.randint(0, 2147483647)
        
        # 이미지 생성
        responses = stability_api.generate(
            prompt=sentence,
            seed=seed,  # 동적으로 변경된 seed 사용
            steps=50,
            cfg_scale=8.0,
            width=1024,
            height=1024,
            samples=min(num_images, 20),  # 최대 샘플 수를 20으로 설정
            sampler=generation.SAMPLER_K_DPMPP_2M,
        )

        # 이미지 저장
        for j, response in enumerate(responses):
            for artifact in response.artifacts:
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img_save_path = os.path.join(image_folder, f"image_{i}_{j}.png")  
                    img.save(img_save_path)
                    print(f"Image saved to {img_save_path}")

    # 이미지를 사용하여 동영상 생성
    image_files = sorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.png')])

    if not image_files:
        print("No images found. Please check the image file path.")
    else:
        first_image = cv2.imread(image_files[0])
        height, width, layers = first_image.shape
        size = (width, height)

        # ffmpeg 실행 파일 경로 지정
        out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

        for image_file in image_files:
            image = cv2.imread(image_file)
            # 이미지를 frame_interval만큼 반복하여 추가합니다.
            for _ in range(frame_interval):
                out.write(image)

        out.release()
        print("Video production completed successfully.")

    # 음성 파일을 동영상에 추가하여 동영상 파일 생성
    audio_clips = [AudioFileClip(os.path.join(audio_folder, f)) for f in os.listdir(audio_folder) if f.endswith('.mp3') or f.endswith('.wav')]
    video_clip = VideoFileClip(output_video_path)
    video_clip = video_clip.set_audio(audio_clips[0])  # 첫 번째 음성 파일 사용
    video_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True, fps=fps)

# 테스트용 이야기 텍스트
story_text = """
Once upon a time, there was a mysterious forest located on the edge of a small village. 
"""

# 음성 파일 폴더 경로
audio_folder = "C:\\Users\\USER\\openai_ex\\audio files"

# 이미지 폴더 경로
image_folder = "generated_images"
# 출력 동영상 경로
output_video_path = "story_video.mp4"
# FPS (프레임 속도)
fps = 1
# 이미지 보여주는 간격 조절을 위한 frame_interval 값 설정 (값이 클수록 이미지 간의 간격이 길어집니다.)
frame_interval = 2

# 영상 생성 함수 호출
generate_video_with_images_and_text(story_text, audio_folder, image_folder, output_video_path, fps, frame_interval)
