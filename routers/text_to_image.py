import os
import io
import warnings
import datetime
from PIL import Image, ImageDraw, ImageFont
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import hashlib
import sys
from stability_sdk import client


# config 모듈의 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


class T2I_generator:
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
    def generator_image(self, prompt: str, korean_prompt: str):
        # 프롬프트에 기반한 시드 값 생성
        unique_seed = self.generate_seed_from_prompt(prompt)
        print(f"Seed for prompt1111111 '{prompt}': {unique_seed}")
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

class T2I_generater_from_prompts:
    def __init__(self, api_key, image_font_path, image_path):
        self.api_key = api_key
        self.image_font_path = image_font_path  # Path 객체를 문자열로 변환
        self.image_path = image_path  # Path 객체를 문자열로 변환

    def generate_images_from_prompts(self, prompts, korean_prompts):
        t2i_gen = T2I_generator(api_key=self.api_key, image_font_path=self.image_font_path, image_path=self.image_path)
        for i, prompt in enumerate(prompts):
            # 한국어 설명을 프롬프트와 함께 이미지 생성 함수에 전달합니다.
            img_path = t2i_gen.generator_image(prompt, korean_prompts[i])
            if img_path:
                print(f"Image for prompt {i} saved to {img_path}")
            else:
                print(f"Failed to generate image for prompt {i}")

