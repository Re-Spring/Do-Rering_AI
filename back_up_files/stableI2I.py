import os
import io
import warnings
from PIL import Image, ImageDraw, ImageFont
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from pathlib import Path
from dotenv import load_dotenv
import random

# .env 파일로부터 환경변수를 불러옴. API 키 같은 중요 정보를 코드 외부에서 관리할 수 있게 해줌.
load_dotenv()

# Stability AI 서버 정보와 API 키를 환경 변수에서 설정.
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
STABILITY_KEY = os.getenv("STABLE_API_KEY")

# Stability AI 클라이언트 초기화. 여기서 API 키를 사용해 서비스에 인증하고, 이미지 생성 엔진을 설정함.
stability_api = client.StabilityInference(
    key=STABILITY_KEY,
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)


class T2I_generator:
    def generator_image(prompt: str, seed_number: int) -> Image.Image:
        # 이미지 생성 요청을 Stability API에 전송. prompt, seed_number 등의 파라미터를 사용하여 이미지 생성 요청을 커스터마이즈함.
        answers = stability_api.generate(
            prompt=prompt,
            seed=seed_number,
            steps=50,
            cfg_scale=8.0,
            width=1024,
            height=1024,
            samples=1,
            sampler=generation.SAMPLER_K_DPMPP_2M
        )

        # 생성된 이미지를 처리. 이미지가 성공적으로 생성되면 이를 반환하고, 그렇지 않으면 None을 반환함.
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn("Your request activated the API's safety filters. Modify the prompt and try again.")
                elif artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    return img

        return None


def add_text_to_image(img: Image.Image, text: str, position: tuple = (10, 10), font_size: int = 100):
    # 이미지에 텍스트를 추가하는 함수. PIL 라이브러리를 사용하여 이미지 상에 원하는 위치와 폰트 크기로 텍스트를 그림.
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    # 지정된 폰트를 사용해 텍스트를 그릴 수 있는 Draw 객체를 생성.
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(img)
    draw.text(position, text, font=font, fill=(255, 255, 255))

    return img


def save_image(img: Image.Image, text: str, seed: int, prompt_index: int, variation_index: int) -> str:
    # 이미지를 파일 시스템에 저장하는 함수. 저장 전에 add_text_to_image 함수를 사용해 이미지에 텍스트를 추가함.
    image_dir = Path(__file__).resolve().parent.parent / "static/text_to_image/images/"
    image_dir.mkdir(parents=True, exist_ok=True)
    img_with_text = add_text_to_image(img, text)
    img_filename = f"prompt_{prompt_index}_variation_{variation_index}_seed_{seed}.png"
    img_path = image_dir / img_filename
    img_with_text.save(img_path)
    return str(img_path)


def generate_images_from_prompts(prompts: list, seed_number: int, num_images_per_prompt: int = 5):
    # 주어진 프롬프트 리스트를 순회하며 각 프롬프트에 대해 여러 이미지를 생성하고 저장하는 함수.
    for i, prompt in enumerate(prompts):
        for j in range(num_images_per_prompt):
            img = T2I_generator.generator_image(prompt, seed_number + j)
            if img:
                img_path = save_image(img, prompt, seed_number + j, i, j)
                print(f"Image for prompt {i} variation {j} saved to {img_path}")
            else:
                print(f"Failed to generate image for prompt {i} variation {j}")


# 이미지 생성을 위한 프롬프트 정의.
prompts = [
    """
# Secret friends in a fairy tale

## a story introduction
Located on the edge of a secluded village, the mysterious forest was filled with the sounds of birds singing and trees dancing. But the villagers said that the forest was so deep and maze-like that no one could go deep. The children always wondered what the secret behind the forest was.

## Roles
- You are a specialized machine that is good at drawing and creating images.

## an audience
- This product is aimed at Python developers who are proficient in image types.

## a task
The ultimate goal is to convert document types into images based on story introductions. To do this, we consider a step-by-step approach. Information about document types can be found in "Document Types" below.

## Step-by-step Instructions (Step)
1. You can use three document titles cited from the site where you searched the model name on the Internet.
2. Referring to the document title, the first image extracts the image cover.
3. Translate the title of the document into English.
4. If you have made a cover with a title, extract the remaining images. However, extract a consistent image. The most helpful thing when extracting an image is the 'action noun'. A behavioral noun means an action or event. It simply means that the root of the word is 'verb.' Words that do not correspond to action nouns are related to brand names, product names, product categories, product types, product characteristics, and more.

## Document Type
- Create an image for each paragraph of the fairy tale content. It visually expresses the story of a fairy tale.

## Policy
- It does not create unnecessary images.
- Extract the image without being crushed.
    """
]

# 고정된 시드 값을 설정하여 이미지 생성의 재현성을 확보.
fixed_seed = random.randint(0, 2 ** 32 - 1)
print(f"{fixed_seed}", "is the fixed seed.")

# 설정된 프롬프트를 사용해 이미지 생성 및 저장을 실행.
generate_images_from_prompts(prompts, fixed_seed)
