import os
import io
import warnings
import datetime
from PIL import Image, ImageDraw, ImageFont
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from pathlib import Path
from dotenv import load_dotenv
import random
import hashlib

# .env 파일에서 환경 변수를 불러오는 부분입니다.
load_dotenv()

# Stability AI 서버 정보와 API 키를 환경 변수에서 설정합니다.
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
STABILITY_KEY = os.getenv("STABLE_API_KEY")

# Stability AI 클라이언트를 초기화합니다. API 키를 사용해 서비스에 인증하고 이미지 생성 엔진을 설정합니다.
stability_api = client.StabilityInference(
    key=STABILITY_KEY,
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)
# 경로 설정 및 필요한 디렉터리 생성
base_dir = Path(__file__).resolve().parent.parent / "static/text_to_image"
image_path = base_dir / "images"
# 폰트 파일의 경로와 이미지를 저장할 폴더의 경로를 올바르게 설정하세요.
image_font_path = base_dir / "font" / "SpoqaHanSansNeo-Light.ttf"

class T2I_generator:
    def __init__(self, font_path: str, image_folder: str):
        self.font_path = str(font_path)  # Path 객체를 문자열로 변환
        self.image_folder = str(image_folder)  # Path 객체를 문자열로 변환
        # 클래스가 초기화될 때 고정 시드 값을 설정합니다.

    def generate_seed_from_prompt(self, prompt: str):
        # SHA-256 해시 함수를 사용하여 프롬프트에 대한 고유한 시드 값을 생성합니다.
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        # 해시값의 앞부분을 정수로 변환하여 시드 값으로 사용
        seed = int(prompt_hash[:8], 16) % (2 ** 32)  # 해시값의 앞부분을 정수로 변환하여 시드 값으로 사용
        return seed
    def generator_image(self, prompt: str, korean_prompt: str):
        # 프롬프트에 기반한 시드 값 생성
        unique_seed = self.generate_seed_from_prompt(prompt)
        print(f"Seed for prompt1111111 '{prompt}': {unique_seed}")
        answers = stability_api.generate(
            prompt=prompt,
            seed=unique_seed,
            steps=50,
            cfg_scale=9.0,
            width=1024,
            height=1024,
            samples=1,
            sampler=generation.SAMPLER_K_DPMPP_2M
        )

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    # 안전 필터에 걸린 경우 경고 메시지를 출력하고 None을 반환합니다.
                    warnings.warn("Your request activated the API's safety filters. Modify the prompt and try again.")
                    return None
                elif artifact.type == generation.ARTIFACT_IMAGE:
                    # 이미지 생성이 성공한 경우, 이미지에 한국어 텍스트를 추가하고 저장합니다.
                    img = Image.open(io.BytesIO(artifact.binary))
                    img_with_text = self.add_text_to_image(img, korean_prompt)
                    image_path = self.save_image(img_with_text, unique_seed, prompt)
                    print(f"Seed for prompt22222222 '{prompt}': {unique_seed}")
                    return image_path
        return None
    # add_text_to_image() 및 save_image() 메서드는 이전과 동일합니다.
    def add_text_to_image(self, img: Image.Image, text: str, position: tuple = (10, 10), font_size: int = 20):
        # 이미지에 텍스트를 추가하는 함수입니다.
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font_path, font_size)
        draw.text(position, text, font=font, fill=(255, 255, 255))
        return img

    def save_image(self, img: Image.Image, seed: int, prompt: str) -> str:
        # 이미지를 지정된 경로에 저장하는 함수입니다.
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        img_filename = f"image_{timestamp}_seed_{seed}.png"
        img_path = os.path.join(self.image_folder, img_filename)
        img.save(img_path)
        return img_path

def generate_images_from_prompts(prompts: list, korean_prompts: list):
    t2i_gen = T2I_generator(font_path=image_font_path, image_folder=image_path)
    for i, prompt in enumerate(prompts):
        # 한국어 설명을 프롬프트와 함께 이미지 생성 함수에 전달합니다.
        img_path = t2i_gen.generator_image(prompt, korean_prompts[i])
        if img_path:
            print(f"Image for prompt {i} saved to {img_path}")
        else:
            print(f"Failed to generate image for prompt {i}")

# 프롬프트와 한국어 설명을 준비합니다.
prompts = [
    "Once upon a time, there was a mystical forest located on the edge of a small village.",
    "This forest was filled with the sounds of birds singing and trees dancing.",
    "However, the villagers thought the forest was too deep and maze-like, so no one dared to venture deep inside.",
    "The children always wondered what secrets the forest held.",
    "Among them, a curious boy named Minjun wanted to uncover the secrets of the forest."
]
korean_prompts = [
"옛날, 작은 마을 가장자리에 신비로운 숲이 있었습니다.",
"이 숲은 새들이 노래하는 소리와 나무들이 춤추는 소리로 가득 찼습니다.",
"하지만, 마을 사람들은 숲이 너무 깊고 미로 같다고 생각해서 아무도 감히 깊은 곳으로 모험하지 못했습니다.",
"아이들은 항상 숲이 어떤 비밀을 품고 있는지 궁금해 했습니다.",
"그 중에서 민준이라는 호기심 많은 소년이 숲의 비밀을 밝혀내고 싶었습니다."
]

# 고정된 시드 값을 설정하여 이미지 생성의 재현성을 확보합니다.
fixed_seed = random.randint(0, 2 ** 32 - 1)
print(f"{fixed_seed}", "is the fixed seed.")

# 설정된 프롬프트를 사용해 이미지 생성 및 저장을 실행합니다.
generate_images_from_prompts(prompts, korean_prompts)
