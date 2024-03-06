import os
import re
import datetime
import librosa
import moviepy.editor as mpy
from PIL import Image, ImageDraw, ImageFont
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import glob
import gc

gc.collect()  # 가비지 컬렉터를 명시적으로 호출
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 설정
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
key = os.environ['STABILITY_KEY']

# 영어 프롬프트와 한글 텍스트를 위한 리스트
english_story_text = [
    "Once upon a time, there was a mystical forest located on the edge of a small village.",
    "This forest was filled with the sounds of birds singing and trees dancing.",
    "However, the villagers thought the forest was too deep and maze-like, so no one dared to venture deep inside.",
    "The children always wondered what secrets the forest held.",
    "Among them, a curious boy named Minjun wanted to uncover the secrets of the forest.",
    "One day, he gathered his courage and set out on an adventure into the depths of the forest.",
    "He carried an old map, a compass, and a small bag.",
    "As Minjun walked deeper into the forest, the trees grew taller, and the flowers became more vibrant.",
    "Suddenly, he saw a small light twinkling through the leaves.",
    "Minjun decided to follow the light."
]

korean_story_text = [
    "옛날 옛적에 작은 마을 가장자리에 신비한 숲이 있었습니다.",
    "이 숲은 새들의 노래소리와 나무들이 춤추는 소리로 가득 차 있었습니다.",
    "그러나 마을 사람들은 숲이 너무 깊고 미로 같다고 생각하여 아무도 깊숙이 들어가려고 하지 않았습니다.",
    "숲에는 무슨 비밀이 숨겨져 있는지, 아이들은 항상 궁금해했습니다.",
    "그중에서도 호기심 많은 소년 민준이는 숲의 비밀을 밝히고 싶어 했습니다.",
    "어느 날, 용기를 내어 깊은 숲속으로 모험을 떠났습니다.",
    "그는 오래된 지도와 나침반, 그리고 작은 가방을 들고 숲속으로 걸음을 옮겼습니다.",
    "민준이가 숲 속을 걷다 보니, 나무들이 점점 더 커지고, 꽃들의 색깔이 더 화려해졌습니다.",
    "그때, 갑자기 나뭇잎 사이로 작은 빛이 반짝이는 것이 보였습니다.",
    "민준이는 그 빛을 따라가 보기로 했습니다."
]


# 이미지 생성 함수
def generate_image_with_stability_ai(english_prompts, korean_prompts, image_folder, api_key, font_path):
    print("generate_image_with_stability_ai", api_key)
    stability_api = client.StabilityInference(
        key=api_key,
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0",
    )
    image_paths = []
    for i, english_prompt in enumerate(english_prompts):
        response = stability_api.generate(
            prompt=english_prompt,
            seed=12345,  # Unique seed for each prompt
            steps=50,
            cfg_scale=8.0,
            width=1024,
            height=1024,
            samples=1,
            sampler=generation.SAMPLER_K_DPMPP_2M
        )
        for resp in response:
            for artifact in resp.artifacts:
                if artifact.type == generation.ARTIFACT_IMAGE:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    image_file_name = f"image_{timestamp}_{i}.png"
                    image_path = os.path.join(image_folder, image_file_name)
                    with open(image_path, 'wb') as f:
                        f.write(artifact.binary)
                    image_paths.append(image_path)
                    # 한글 텍스트 추가
                    add_text_to_image(image_path, korean_prompts[i], (30, 30), font_path, 24, (255, 255, 255))
    return image_paths


# 이미지에 텍스트 추가 함수
def add_text_to_image(image_path, text, position, font_path, font_size, color=(255, 255, 255)):
    try:
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, font_size)
        draw.text(position, text, fill=color, font=font)
        image.save(image_path)
    except Exception as e:
        print(f"Error adding text to image: {e}")


# 오디오 파일 길이 확인 함수
def get_audio_length(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)
        return librosa.get_duration(y=y, sr=sr)
    except Exception as e:
        print(f"Error getting audio length: {e}")
        return 0


# 비디오 생성 함수
def generate_video_with_images_and_text(english_story_text, korean_story_text, audio_folder, image_folder,
                                        output_video_path, key, font_path, fps=1):
    print("image_folder2", image_folder)
    image_paths = generate_image_with_stability_ai(english_story_text, korean_story_text, image_folder, key, font_path)
    video_clips = []
    audio_files = sorted(glob.glob(os.path.join(audio_folder, '*.mp3')), key=os.path.getmtime)
    if not audio_files:
        print("No audio files found.")
        return

    for i, img_path in enumerate(image_paths):
        if i < len(audio_files):
            audio_file = audio_files[i]
            audio_length = get_audio_length(audio_file)
            clip = mpy.ImageClip(img_path).set_duration(audio_length)
            audio_clip = mpy.AudioFileClip(audio_file).set_duration(audio_length)
            clip = clip.set_audio(audio_clip)
            video_clips.append(clip)

    if video_clips:
        final_clip = mpy.concatenate_videoclips(video_clips, method="compose")
        final_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=fps)
        final_clip.close()
    else:
        print("Failed to generate video clips.")


# C:\Dorering project\Do-Rering_AI\T2I\fairytale.py
# .\fairytale.py
# 경로 설정 및 필요한 디렉터리 생성
base_dir = os.path.dirname(os.path.abspath(__file__))
print(base_dir)
image_folder = 'static\\T2I\\generated_images'
print("image_folder1", image_folder)
audio_folder = 'static\\T2I\\audio_files'
output_video_path = 'static\\T2I\\movies\\output_video.mp4'
font_path = 'static\\T2I\\font\\Pretendard-Black.ttf'

os.makedirs(image_folder, exist_ok=True)
os.makedirs(audio_folder, exist_ok=True)
os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

# 스크립트 실행

generate_video_with_images_and_text(english_story_text, korean_story_text, audio_folder, image_folder,
                                    output_video_path, key, font_path, fps=1)
