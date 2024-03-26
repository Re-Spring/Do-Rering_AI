import os
import io
import warnings
from datetime import datetime

from ai_modules.deepl_ai import Deepl_api
import random
from PIL import Image, ImageDraw, ImageFont
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import sys
from stability_sdk import client
from pathlib import Path
from config import DEEPL_API_KEY, initial_image_path
from rembg import remove

deepl_module = Deepl_api(api_key=DEEPL_API_KEY)

# config 모듈의 경로를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

class Text_to_image:
    def __init__(self, api_key, image_font_path, image_path, character_image_path):
        self.api_key = api_key
        self.font_path = image_font_path  # Path 객체를 문자열로 변환
        self.image_folder = image_path  # Path 객체를 문자열로 변환
        self.character_image_path = character_image_path
        self.stability_api = client.StabilityInference(
            key=self.api_key,
            verbose=True,
            engine="stable-diffusion-xl-1024-v1-0",
        )

    def character_image(self, title, eng_title, user_id):
        seed = random.randint(2224400000, 2224499999)
        try:
            initial_image = Image.open(initial_image_path)
        except FileNotFoundError:
            initial_image = Image.new("RGB", (1024, 1024), (0, 0, 0))

        answers = self.stability_api.generate(
            prompt=[
                generation.Prompt(
                    text=f"{eng_title} ,ghibli style, bangs, long sleeves, no glasses,necklace, parted lips, smile, solo, alone, one person, white background, male focus, looking at viewer, ((masterpiece)) <lora:ghibli_style:0.65>",
                    parameters=generation.PromptParameters(weight=2)),
                generation.Prompt(
                    text="worst quality, normal quality, error, low quality, text, watermark, logo, ugly, bad anatomy, blurry, bad hands, username, three hands, three legs, bad arms, missing legs, missing arms, poorly drawn face, bad face, fused face, cloned face, worst face, three crus, extra crus, fused crus, worst feet, three feet, fused feet, fused thigh, three thigh, fused thigh, extra thigh, worst thigh, missing fingers, extra fingers, ugly fingers, long fingers, hom, extra eyes, huge eyes, Posts, bad anatomy",
                    parameters=generation.PromptParameters(weight=-2))
                ],
            init_image=initial_image,
            seed=seed,
            steps=20,
            width=1024,
            height=1024,
            samples=1,
            cfg_scale=8,
            guidance_prompt="""8k, best quality, masterpiece, ultra detail, cute face, smile, beautiful detailed eyes, 7-year-old Korean, pretty, smooth lighting, cinematic lighting, distinct face""",
            guidance_strength=0.5,
            guidance_models=["clip_vit_base_patch16_384", "clip_vit_base_patch16_384"]
        )

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    # 안전 필터에 걸린 경우 경고 메시지를 출력하고 None을 반환합니다.
                    warnings.warn("Your request activated the API's safety filters. Modify the prompt and try again.")
                elif artifact.type == generation.ARTIFACT_IMAGE:
                    # 이미지 생성이 성공한 경우, 이미지에 한국어 텍스트를 추가하고 저장합니다.
                    img = Image.open(io.BytesIO(artifact.binary))
                    img = remove(img)
                    character_image_path = self.save_character_image(img, title)
                    return img, seed, character_image_path


    def title_image(self, eng_title: str, title: str, user_id, seed) -> (Image.Image, int, str):
        print(f"타이틀 생성 시작 =================== {title}")
        # 고정 시드를 생성하는 메서드입니다.
        prompt = f"{eng_title}"
        try:
            initial_image = Image.open(initial_image_path)  # PIL.Image.Image 이미지 객체로 변환
        except FileNotFoundError:
            warnings.warn(f"Initial image not found at {initial_image_path}.")
            initial_image = Image.new("RGB", (1024, 1024), (0, 0, 0))
        print(f"이미지 생김새 : {initial_image}")

        answers = self.stability_api.generate(
            prompt=[
                    generation.Prompt(text="init_image is main character of fairytale", parameters=generation.PromptParameters(weight=2.0)),
                    generation.Prompt(text=f"{prompt}, Please use the main character to make a cover of the fairytale, No protagonist changes",parameters=generation.PromptParameters(weight=1.9)),
                    generation.Prompt(text="worst quality, normal quality, low quality, text, watermark, logo, ugly, bad anatomy, bad hands, three hands, three legs, bad arms, missing legs, missing arms, poorly drawn face, bad face, fused face, cloned face, worst face, three crus, extra crus, fused crus, worst feet, three feet, fused feet, fused thigh, three thigh, fused thigh, extra thigh, worst thigh, missing fingers, extra fingers, ugly fingers, long fingers, hom, extra eyes, huge eyes, Posts ",parameters=generation.PromptParameters(weight=-2))
                    ],
            init_image=initial_image,
            seed=seed,
            steps=50,
            width=1024,
            height=1024,
            samples=1,
            cfg_scale=8,
            guidance_prompt="""8k, best quality, masterpiece, ultra detail, cute face, smile, beautiful detailed eyes, 7-year-old Korean, pretty, smooth lighting, cinematic lighting, close-up""" ,
            guidance_strength=0.4,
            guidance_models=["clip_vit_base_patch16_384", "clip_vit_base_patch16_384"]

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
                    return img, seed, image_path  # Return the PIL.Image object directly
    def story_image(self, no_title_ko_pmt: str, no_title_eng_pmt: str, title: str, user_id, page: int, initial_seed) -> str:
        print(f"이야기 생성 시작 ======================== {page}")

        try:
            initial_image = Image.open(initial_image_path)  # PIL.Image.Image 이미지 객체로 변환
        except FileNotFoundError:
            warnings.warn(f"Initial image not found at {initial_image_path}.")
            initial_image = Image.new("RGB", (1024, 1024), (0, 0, 0))

        prompt = f"{no_title_eng_pmt}"
        answers = self.stability_api.generate(
            prompt=[
                    generation.Prompt(text="init_image is main character of fairytale", parameters=generation.PromptParameters(weight=2.0)),
                    generation.Prompt(text="the same type of painting as that of the main character, Create an image according to the story", parameters=generation.PromptParameters(weight=1.8)),
                    generation.Prompt(text=f"story:{prompt}, anime style, No protagonist changes",parameters=generation.PromptParameters(weight=1.0)), # 긍정 프롬프트 추가
                    generation.Prompt(text="worst quality, normal quality, low quality, text, watermark, logo, ugly, bad anatomy, bad hands, three hands, three legs, bad arms, missing legs, missing arms, poorly drawn face, bad face, fused face, cloned face, worst face, three crus, extra crus, fused crus, worst feet, three feet, fused feet, fused thigh, three thigh, fused thigh, extra thigh, worst thigh, missing fingers, extra fingers, ugly fingers, long fingers, hom, extra eyes, huge eyes, Posts,",parameters=generation.PromptParameters(weight=-2)) # 부정 프롬프트
                    ],
            init_image=initial_image,
            seed=initial_seed,
            steps=50,
            cfg_scale=8.0,
            width=1024,
            height=1024,
            samples=1,
            guidance_prompt="""8k, best quality, masterpiece, ultra detail, cute face, smile, beautiful detailed eyes, 7-year-old Korean, pretty, smooth lighting, cinematic lighting, close-up""" ,
            guidance_strength=0.4,
            guidance_models=["clip_vit_base_patch16_384", "clip_vit_base_patch16_384"]
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
                    print(f"이야기 생성 종료 ======================== {initial_seed}")
                    return image_path
            return None

    # add_text_to_image() 및 save_image() 메서드는 이전과 동일합니다.
    def add_text_to_image(self, img: Image.Image, text: str, position: tuple = (10, 10), font_size: int = 25):
        # 이미지에 텍스트를 추가하는 함수입니다.
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(self.font_path, font_size)
        draw.text(position, text, font=font, fill=(255, 255, 255))
        return img

    def save_character_image(self, img: Image.Image, title) -> str:
        now = datetime.now()
        now = now.strftime('%y%m%d%H%M%S')
        character_img_name = f"{title}_{now}.png"
        character_filename = os.path.join(self.character_image_path, character_img_name)
        save_image_path = Path(self.character_image_path)

        if not save_image_path.exists():
            save_image_path.mkdir(parents=True)

        img.save(character_filename)
        return character_filename


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
    def __init__(self, api_key, image_font_path, image_path, character_image_path):
        self.api_key = api_key
        self.image_font_path = image_font_path  # Path 객체를 문자열로 변환
        self.image_path = image_path  # Path 객체를 문자열로 변환
        self.character_image_path = character_image_path

    def title_images_from_prompt(self, eng_title, title, user_id, seed):
        t2i_gen = Text_to_image(api_key=self.api_key, image_font_path=self.image_font_path, image_path=self.image_path, character_image_path=self.character_image_path)
        img_path = t2i_gen.title_image(eng_title, title, user_id=user_id, seed=seed)
        return img_path

    def story_images_from_prompts(self, no_title_ko_pmt, no_title_eng_pmt, title, user_id, initial_seed):
        # Text_to_image 클래스의 인스턴스 생성
        t2i_gen = Text_to_image(api_key=self.api_key, image_font_path=self.image_font_path, image_path=self.image_path, character_image_path=self.character_image_path)

        image_paths = []  # 생성된 이미지 파일의 경로를 저장할 리스트
        for i, prompt in enumerate(no_title_ko_pmt):
            # 한국어 설명을 프롬프트와 함께 이미지 생성 함수에 전달합니다.
            # 이미지 생성 함수를 호출하여 이미지를 생성하고 해당 이미지의 경로를 받아옵니다.
            page = i + 1
            img_path = t2i_gen.story_image(no_title_ko_pmt[i], no_title_eng_pmt[i], title, user_id=user_id, page=page, initial_seed=initial_seed)
            # 이미지 생성이 성공하면 이미지 경로를 출력하고, 실패하면 실패 메시지를 출력합니다.
            if img_path:
                image_paths.append(img_path)  # 이미지 파일 경로를 리스트에 추가
                print(f"Image for prompt {i} saved to {img_path}")
            else:
                print(f"Failed to generate image for prompt {i}")
        return image_paths  # 생성된 이미지 파일의 경로를 반환합니다.