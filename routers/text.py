import os
import datetime
from pathlib import Path
import random
import librosa
import moviepy.editor as mpy
from PIL import Image, ImageDraw, ImageFont
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import gc
from dotenv import load_dotenv

gc.collect()  # 가비지 컬렉터를 명시적으로 호출

load_dotenv()

# 환경 변수 설정
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
STABILITY_KEY = os.getenv("STABILITY_KEY")
print("STABILITY_KEY", STABILITY_KEY)


class TextToImage:
    def __init__(self, english_story_text, korean_story_text, audio_dir, image_dir, output_video_dir, font_dir, key):
        self.english_story_text = english_story_text
        self.korean_story_text = korean_story_text
        self.audio_dir = audio_dir
        self.image_dir = image_dir
        self.output_video_dir = output_video_dir
        self.font_dir = font_dir
        self.key = key

    # 이미지 생성 함수
    def generate_image_with_stability_ai(self, english_prompts: str, korean_prompts, image_folder, STABILITY_KEY,
                                         font_path):
        print("generate_image_with_stability_ai", STABILITY_KEY)
        stability_api = client.StabilityInference(
            key=STABILITY_KEY,
            verbose=True,
            engine="stable-diffusion-xl-1024-v1-0",
        )
        base_seed = random.randint(0, 2 ** 32 - 1)  # 고정된 기본 시드 값
        print("base_seed", base_seed)

        image_paths = []
        num_images = min(10, len(english_prompts))  # 최대 10개 이미지 생성
        for i, english_prompt in enumerate(english_prompts):
            modified_seed = base_seed + i  # 각 이미지마다 시드 값을 조금씩 변경
            print(f"Generating image for paragraph {i + 1} with seed {modified_seed}")
            prompt_index = i % len(english_prompts)  # 프롬프트 리스트를 반복 사용
            response = stability_api.generate(
                prompt=english_prompts[prompt_index],
                seed=modified_seed,  # Unique seed for each prompt
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
                        self.add_text_to_image(image_path, korean_prompts[i], (30, 30), font_path, 24, (255, 255, 255))
        return image_paths

    # 이미지에 텍스트 추가 함수
    def add_text_to_image(self, image_path, text, position, font_path, font_size, color=(255, 255, 255)):
        try:
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font_path, font_size)
            draw.text(position, text + " ", fill=color, font=font),
            image.save(image_path),
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
def generate_video_with_images_and_text(english_prompts, korean_prompts, audio_folder, image_folder,
                                        output_video_path, STABILITY_KEY, font_path, fps=1):
    try:
        # 이미지 생성
        t2i = TextToImage(english_prompts, korean_prompts, audio_folder, image_folder, output_video_path, font_path,
                          STABILITY_KEY)
        print("T@I 이미지 : ", t2i)
        image_paths = t2i.generate_image_with_stability_ai(english_prompts, korean_prompts, image_folder, STABILITY_KEY,
                                                           font_path)
        print("이미지 패스 경로 : ", image_paths)
        # 오디오 파일 경로
        audio_path = os.path.join(audio_folder, f"{random}.wav")
        print("오디오 경로 : ", audio_path)
        # 오디오 길이
        audio_length = get_audio_length(audio_path)
        print("오디오 길이 : ", audio_length)
        # 비디오 생성
        video = mpy.VideoFileClip(image_paths[0]).set_duration(audio_length)
        print("비디오 : ", video)
        video = video.set_fps(fps)
        print("비디오 fps : ", video)
        video = video.set_audio(mpy.AudioFileClip(audio_path))
        print("비디오 오디오 : ", video)
        video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a",
                              remove_temp=True, verbose=False)
        print(f"Video saved to {output_video_path}")
    except Exception as e:
        print(f"Error generating video: {e}")


# 경로 설정 및 필요한 디렉터리 생성
base_dir = Path(__file__).resolve().parent.parent / "static/text_to_image"
# 기준 경로를 사용하여 각 폴더의 경로를 설정
image_dir = base_dir / "images"
audio_dir = base_dir / "audio"
output_video_dir = base_dir / "movies"
font_dir = base_dir / "font"

# 필요한 폴더들이 없다면 생성
image_dir.mkdir(parents=True, exist_ok=True)
audio_dir.mkdir(parents=True, exist_ok=True)
output_video_dir.mkdir(parents=True, exist_ok=True)
font_dir.mkdir(parents=True, exist_ok=True)

# 최종 경로들을 문자열로 출력 (필요에 따라 사용)
print(f"Image Directory: {image_dir}")
print(f"Audio Directory: {audio_dir}")
print(f"Output Video Directory: {output_video_dir}")
print(f"Font Directory: {font_dir}")

# 파일 경로 설정 (예: 출력 비디오 파일 및 폰트 파일)
output_video_path = output_video_dir / "output_video.wav"
font_path = font_dir / "Pretendard-Black.ttf"

# 영어 프롬프트와 한글 텍스트를 위한 리스트
english_story_text = [
    """
    ## Roles
    - You are a specialized machine that is good at drawing and creating images.

    ## Task
    - The ultimate goal is to convert document types into images based on story introductions. To do this, we consider a step-by-step approach. Information about document types can be found in "Document Types" below.

    # Story introduction
    ## Step-by-step Instructions
    Step 1. Once upon a time, there was a mystical forest located on the edge of a small village.
    Step 2. This forest was filled with the sounds of birds singing and trees dancing.
    Step 3. However, the villagers thought the forest was too deep and maze-like, so no one dared to venture deep inside.
    Step 4. The children always wondered what secrets the forest held.
    Step 5. Among them, a curious boy named Minjun wanted to uncover the secrets of the forest.

    """
]

korean_story_text = [
    "옛날 옛적에 작은 마을 가장자리에 신비한 숲이 있었습니다.",
    "이 숲은 새들의 노래소리와 나무들이 춤추는 소리로 가득 차 있었습니다.",
    "그러나 마을 사람들은 숲이 너무 깊고 미로 같다고 생각하여 아무도 깊숙이 들어가려고 하지 않았습니다.",
    "숲에는 무슨 비밀이 숨겨져 있는지, 아이들은 항상 궁금해했습니다.",
    "그 중에서도 호기심 많은 소년 민준은 숲의 비밀을 밝혀내고 싶어했습니다.",
]

# 설정된 프롬프트를 사용해 이미지 생성 및 저장을 실행.
generate_video_with_images_and_text(english_story_text, korean_story_text, audio_dir, image_dir,
                                    output_video_path, STABILITY_KEY, font_path, fps=1)
