import os
import re
import warnings
import moviepy.editor as mpy
from PIL import Image, ImageDraw, ImageFont
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import datetime

# 환경 변수 설정
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = "sk-mEarfBLblMX2zZc6eJ3032Is4smpsefMRKjPafXsI6Xw94EA"

def generate_image_with_stability_ai(prompt, image_folder):
    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_KEY'],
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0",
    )
    # 반복
    answers = stability_api.generate(
        prompt=["Once upon a time, there were friends living in a forgotten little village."],
        seed=4253978046,
        steps=50,
        cfg_scale=8.0,
        width=1024,
        height=1024,
        samples=1,
        sampler=generation.SAMPLER_K_DPMPP_2M
    )

    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn("Your request activated the API's safety filters and could not be processed. Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                # 이미지 파일 이름 생성
                image_file_name = f"{artifact.seed}.png"
                # 이미지 저장 경로 결합
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                image_file_name = f"image_{timestamp}_{artifact.seed}.png"
                image_path = os.path.join(image_folder, image_file_name)
                with open(image_path, 'wb') as f:
                    f.write(artifact.binary)
                return image_path
            
def add_text_to_image(image_path, text, position, font_path, font_size, color=(255, 255, 255)):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, fill=color, font=font)
    image.save(image_path)

def sort_files_by_number(file_list):
    return sorted(file_list, key=lambda x: int(re.findall(r'\d+', x)[0]))

def generate_video_with_images_and_text(story_text, audio_folder, image_folder, output_video_path, font_path, fps=1, frame_interval=10):
    sentences = story_text
    video_clips = []

    for sentence in sentences:
        sentence.strip().split('.')
        if not sentence.strip():
            continue
        # 이미지 생성 및 파일 경로 반환
        image_path = generate_image_with_stability_ai(sentence, image_folder)
        print(image_path)
        # 반환된 이미지 파일 경로를 사용하여 한글 텍스트 추가
        text = sentence
        position = (30, 30)
        font_size = 24
        add_text_to_image(image_path, text, position, font_path, font_size)
##
        # 비디오 클립 생성 및 추가
        clip = mpy.ImageClip(image_path).set_duration(frame_interval)
        video_clips.append(clip)
        final_clip = mpy.concatenate_videoclips(video_clips, method="compose")
        
        # 오디오 파일 결합
    audio_files = [os.path.join(audio_folder, f) for f in sorted(os.listdir(audio_folder), key=lambda x: int(re.findall(r'\d+', x)[0]))]
    audio_clips = [mpy.AudioFileClip(audio_file) for audio_file in audio_files]
    final_audio = mpy.concatenate_audioclips(audio_clips)
    final_clip = final_clip.set_audio(final_audio)
        
        #최종 비디오 파일 저장
    final_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=fps)
    
    
# 환경 설정 및 실행 코드
font_path = 'C:\\Dorering project\\Do-Rering_AI\\static\\T2I\\font\\Pretendard-Black.ttf'
audio_folder = 'C:\\Dorering project\\Do-Rering_AI\\static\\T2I\\audio files'
story_text = ["옛날 옛적 잊혀진 작은 마을에 사는 친구들이 있었습니다"]
image_folder = 'C:\\Dorering project\\Do-Rering_AI\\static\\T2I\\generated_images'
output_video_path = 'C:\\Dorering project\\Do-Rering_AI\\static\\T2I\\StoryMovie.mp4'

# 필요한 폴더 생성
os.makedirs(image_folder, exist_ok=True)
os.makedirs(os.path.dirname(output_video_path), exist_ok=True)

# 함수 실행
generate_video_with_images_and_text(story_text, audio_folder, image_folder, output_video_path, font_path)

