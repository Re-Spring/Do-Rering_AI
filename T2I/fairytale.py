import os
import re
import datetime
import librosa
import moviepy.editor as mpy
from PIL import Image, ImageDraw, ImageFont
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import glob
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

# 환경 변수 설정
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = "sk-mEarfBLblMX2zZc6eJ3032Is4smpsefMRKjPafXsI6Xw94EA"


def generate_image_with_stability_ai(prompt, image_folder):
    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_KEY'],
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0",
    )
    image_paths = []
    for i, sentence in enumerate(prompt):
        response = stability_api.generate(
            prompt=sentence,
            seed=4253978046 + i,  # Unique seed for each prompt
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
                    image_path = image_path.replace("\\","/")
                    with open(image_path, 'wb') as f:
                        f.write(artifact.binary)
                    image_paths.append(image_path)
    return image_paths



def add_text_to_image(image_path, text, position, font_path, font_size, color=(255, 255, 255)):
    for name in image_path:
        image = Image.open(name)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, font_size)
        draw.text(position, text, fill=color, font=font)
        print("add_text_to_image",name)
        # image_path = image_path.replace("\\","/")
        print(image_path)
        # image.save(image_path)

def get_audio_length(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    return librosa.get_duration(y=y, sr=sr)

def generate_video_with_images_and_text(story_text, audio_folder, image_folder, output_video_path, font_path, fps=1):
    image_path = generate_image_with_stability_ai(story_text, image_folder)
    video_clips = []
    audio_files = sorted(os.listdir(audio_folder))  # 오디오 파일 정렬

    for i, text in enumerate(story_text):
        if not image_path:
            print("No recent image found.")
            continue

        # 이미지에 텍스트 추가
        text = story_text[i] if i < len(story_text) else ""
        add_text_to_image(image_path, text, (30, 30), font_path, 24)

         
        # 오디오 파일 준비 및 비디오 클립 생성
        if i < len(audio_files):
            audio_file = os.path.join(audio_folder, audio_files[i])
            audio_length = get_audio_length(audio_file)
            clip = mpy.ImageClip(image_path).set_duration(audio_length)
            audio_clip = mpy.AudioFileClip(audio_file).set_duration(audio_length)
            clip = clip.set_audio(audio_clip)
            video_clips.append(clip)
            
        # 비디오 클립 생성 및 오디오 설정
        clip = mpy.ImageClip(image_path).set_duration(audio_length)
        audio_clip = mpy.AudioFileClip(audio_file)
        clip = clip.set_audio(audio_clip)
        video_clips.append(clip)

    # 비디오 클립들을 합쳐 최종 비디오 파일 생성
    if video_clips:
        final_clip = mpy.concatenate_videoclips(video_clips, method="compose")
        output_video_path = output_video_path.replace("\\","/")
        final_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=fps)
    else:
        print("No video clips were generated.")

def test_print(audio_folder, image_folder, font_path, output_video_path) :
    print("audio_folder : ", audio_folder)
    print("image_folder : ", image_folder)
    print("font_path : ", font_path)
    print("output_video_path", output_video_path)

# 환경 설정 및 실행 코드
# font_path = 'static/text_to_image/font/Pretendard-Black.ttf'
# audio_folder = "static/text_to_image/audio_files"
# image_folder = 'static/text_to_image/generated_images'
# output_video_path = 'static/text_to_image/StoryMovie.mp4'
    
# 현재 스크립트 파일의 절대 경로를 가져옵니다.
script_dir = os.path.dirname(os.path.abspath(__file__)).replace("text_to_image","")
audio_folder = os.path.join(script_dir, "static", "text_to_image", "audio_files").replace("\\","/")
image_folder = os.path.join(script_dir, "static", "text_to_image", "generated_images").replace("\\","/")
font_path = os.path.join(script_dir, "static", "text_to_image", "font", "Pretendard-Black.ttf").replace("\\","/")
output_video_path = os.path.join(script_dir, "static", "text_to_image", "StoryMovie.mp4").replace("\\","/")

# 사용 예시
image_path = 'static/text_to_image/generated_images'
text = "옛날 옛적, 작은 마을 가장자리에 위치한 신비한 숲이 있었습니다. 이 숲은 새들이 노래하는 소리와 나무들이 춤추는 모습으로 가득 차 있었지요. 하지만 마을 사람들은 숲이 너무 깊고 미로 같아서 아무도 그 안으로 깊숙이 들어가 보지 못했습니다. 숲에는 무슨 비밀이 숨겨져 있는지, 아이들은 항상 궁금해했습니다."
position = (50, 50)  # 텍스트를 추가할 위치
# font_path = 'static/text_to_image/font/Pretendard-Black.ttf'  # 한글을 지원하는 폰트 파일 경로
font_size = 24
color = (255, 255, 255)  # 텍스트 색상, 여기서는 흰색

story_text = [
    "Once upon a time, there were friends living in a forgotten little village.",
    "This forest was filled with the sounds of birds singing and the sight of trees dancing.",
    "However, the villagers never ventured deep into the forest because it was too dense and maze-like."
]

os.makedirs(image_folder, exist_ok=True)
os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

generate_video_with_images_and_text(story_text, audio_folder, image_folder, output_video_path, font_path)


