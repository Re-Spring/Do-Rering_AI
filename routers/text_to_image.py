import os
import io
import warnings
import datetime
from PIL import Image, ImageDraw, ImageFont
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import hashlib
import sys
from stability_sdk import client
from pathlib import Path


# config 모듈의 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


class Text_to_image:
    def __init__(self, api_key, image_font_path, image_path):
        self.api_key = api_key
        self.font_path = image_font_path  # Path 객체를 문자열로 변환
        self.image_folder = image_path  # Path 객체를 문자열로 변환
        self.stability_api = client.StabilityInference(
            key=self.api_key,
            verbose=True,
            engine="stable-diffusion-xl-1024-v1-0",
        )

    # 클래스가 초기화될 때 고정 시드 값을 설정합니다.
    def generate_seed_from_prompt(self, prompt: str):
        # SHA-256 해시 함수를 사용하여 프롬프트에 대한 고유한 시드 값을 생성합니다.
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        # 해시값의 앞부분을 정수로 변환하여 시드 값으로 사용
        seed = int(prompt_hash[:8], 16) % (2 ** 32)  # 해시값의 앞부분을 정수로 변환하여 시드 값으로 사용
        return seed

    def generator_image(self, prompt: str, korean_prompt: str, title: str):
        # 프롬프트에 기반한 시드 값 생성
        unique_seed = self.generate_seed_from_prompt(prompt)
        answers = self.stability_api.generate(
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
                    image_path = self.save_image(img_with_text, title)
                    return image_path
        return None
    # add_text_to_image() 및 save_image() 메서드는 이전과 동일합니다.
    def add_text_to_image(self, img: Image.Image, text: str, position: tuple = (10, 10), font_size: int = 17):
        # 이미지에 텍스트를 추가하는 함수입니다.
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font_path, font_size)
        draw.text(position, text, font=font, fill=(255, 255, 255))
        return img

    def save_image(self, img: Image.Image, title: str ) -> str:
        # 이미지를 지정된 경로에 저장하는 함수입니다.
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        img_path = f"{title}"
        img_filepath = Path(os.path.join(self.image_folder, img_path))
        img_filename = os.path.join(self.image_folder, f"{title}_{timestamp}.png")
        if img_filepath.exists():
            img_filepath.mkdir(parents = True)
        img.save(img_filename)
        img_path = str(img_filename)
        return img_path

class T2I_generater_from_prompts:
    def __init__(self, api_key, image_font_path, image_path):
        self.api_key = api_key
        self.image_font_path = image_font_path  # Path 객체를 문자열로 변환
        self.image_path = image_path  # Path 객체를 문자열로 변환

    def generate_images_from_prompts(self, english_prompts, korean_prompts, title):
        # Text_to_image 클래스의 인스턴스 생성
        t2i_gen = Text_to_image(api_key=self.api_key, image_font_path=self.image_font_path, image_path=self.image_path)
        # 영어 프롬프트와 한국어 프롬프트를 반복하여 이미지 생성 함수에 전달
        image_paths = []  # 생성된 이미지 파일의 경로를 저장할 리스트
        for i, prompt in enumerate(english_prompts):
            # 한국어 설명을 프롬프트와 함께 이미지 생성 함수에 전달합니다.
            # 이미지 생성 함수를 호출하여 이미지를 생성하고 해당 이미지의 경로를 받아옵니다.
            img_path = t2i_gen.generator_image(english_prompts[i], korean_prompts[i], title)
            # 이미지 생성이 성공하면 이미지 경로를 출력하고, 실패하면 실패 메시지를 출력합니다.
            if img_path:
                image_paths.append(img_path)  # 이미지 파일 경로를 리스트에 추가
                print(f"Image for prompt {i} saved to {img_path}")
            else:
                print(f"Failed to generate image for prompt {i}")
        return image_paths  # 이미지 파일 경로 목록 반환

# class Stability_video_generate:
#     def __init__(self):
