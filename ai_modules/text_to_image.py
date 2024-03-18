import os
import io
import warnings
from ai_modules.deepl_ai import Deepl_api
import random
from PIL import Image, ImageDraw, ImageFont
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import sys
from stability_sdk import client
from pathlib import Path

from config import DEEPL_API_KEY

deepl_module = Deepl_api(api_key=DEEPL_API_KEY)

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
        self.fixed_seed = self.generate_fixed_seed()

    # 클래스가 초기화될 때 고정 시드 값을 설정합니다.
    def generate_fixed_seed(self):
        return random.randint(0, 2 ** 32 - 1)

    def title_image(self, eng_title: str, title: str, user_id) -> (Image.Image, int):
        print(f"타이틀 생성 시작 =================== {title}")

        seed = self.fixed_seed
        print(f"Seed 값 ========== : {seed}")
        positive_prompt = f"""
        
        "Imagine a fairy tale world that a seven-year-old child can see."
        "Imagine a beautiful scene that matches the title: {eng_title}"
        
        """

        answers = self.stability_api.generate(
            prompt=positive_prompt,
            seed=seed,
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
                elif artifact.type == generation.ARTIFACT_IMAGE:
                    # 이미지 생성이 성공한 경우, 이미지에 한국어 텍스트를 추가하고 저장합니다.
                    img = Image.open(io.BytesIO(artifact.binary))
                    img_with_text = self.add_text_to_image(img, title)
                    image_path = self.save_image(img_with_text, title, user_id)
                    print(f"타이틀 생성 종료 ====================== {seed}")
                    return img, seed,image_path  # Return the PIL.Image object directly
                    # return image_path

    def story_image(self, no_title_ko_pmt: str, no_title_eng_pmt: str, title: str, user_id, page: int) -> str:
        print(f"이야기 생성 시작 ========================{page}")

        # title_image 함수의 반환값을 img_tuple에 할당합니다.
        img_tuple = self.title_image(no_title_eng_pmt, title, user_id)
        if img_tuple is None:
            return None

        # img_tuple에서 이미지 객체와 시드 값을 추출합니다.
        img, seed, _ = img_tuple
        negative_prompt = f"""
        
        Create an image by changing the background without changing the protagonist of the image.: {no_title_eng_pmt}
        
        """

        answers = self.stability_api.generate(
            prompt=negative_prompt,
            init_image=img,  # Assign our previously generated img as our Initial Image for transformation.
            seed=seed,
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
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img_with_text = self.add_text_to_image(img, no_title_ko_pmt)
                    image_path = self.save_image(img_with_text, title, user_id, page)
                    print(f"이야기 생성 종료 ========================{seed}")
                    return image_path
        return None

    # add_text_to_image() 및 save_image() 메서드는 이전과 동일합니다.
    def add_text_to_image(self, img: Image.Image, text: str, position: tuple = (10, 10), font_size: int = 25):
        # 이미지에 텍스트를 추가하는 함수입니다.
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font_path, font_size)
        draw.text(position, text, font=font, fill=(255, 255, 255))
        return img

    def save_image(self, img: Image.Image, title: str, user_id, page=None) -> str:
        # 이미지를 지정된 경로에 저장하는 함수입니다.
        img_path = f"{user_id}/{title}"
        img_filepath = Path(os.path.join(self.image_folder, img_path))

        filename = f"{user_id}/{title}/{title}{('_' + str(page) + 'Page') if page else ''}.png"
        img_filename = os.path.join(self.image_folder, filename)

        if not img_filepath.exists():
            img_filepath.mkdir(parents=True)

        img.save(img_filename)
        return img_filename

class T2I_generater_from_prompts:
    def __init__(self, api_key, image_font_path, image_path):
        self.api_key = api_key
        self.image_font_path = image_font_path  # Path 객체를 문자열로 변환
        self.image_path = image_path  # Path 객체를 문자열로 변환

    def title_images_from_prompt(self, eng_title, title, user_id):
        t2i_gen = Text_to_image(api_key=self.api_key, image_font_path=self.image_font_path, image_path=self.image_path)
        img_path = t2i_gen.title_image(eng_title, title, user_id=user_id)
        return img_path

    def story_images_from_prompts(self, no_title_ko_pmt, no_title_eng_pmt, title, user_id):
        # Text_to_image 클래스의 인스턴스 생성
        t2i_gen = Text_to_image(api_key=self.api_key, image_font_path=self.image_font_path, image_path=self.image_path)

        image_paths = []  # 생성된 이미지 파일의 경로를 저장할 리스트
        for i, prompt in enumerate(no_title_ko_pmt):
            # 한국어 설명을 프롬프트와 함께 이미지 생성 함수에 전달합니다.
            # 이미지 생성 함수를 호출하여 이미지를 생성하고 해당 이미지의 경로를 받아옵니다.
            print(f"이미지 생성 중 : {i}")
            page = i + 1
            img_path = t2i_gen.story_image(no_title_ko_pmt[i], no_title_eng_pmt[i], title, user_id=user_id, page=page)
            # 이미지 생성이 성공하면 이미지 경로를 출력하고, 실패하면 실패 메시지를 출력합니다.
            if img_path:
                image_paths.append(img_path)  # 이미지 파일 경로를 리스트에 추가
                print(f"Image for prompt {i} saved to {img_path}")
            else:
                print(f"Failed to generate image for prompt {i}")
        return image_paths  # 생성된 이미지 파일의 경로를 반환합니다.