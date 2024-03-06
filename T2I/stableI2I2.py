import os
import io
import warnings
from PIL import Image, ImageDraw, ImageFont
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from pathlib import Path
from dotenv import load_dotenv
import random

# .env 파일에서 환경 변수 불러오기
load_dotenv()

# 환경 변수 설정
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
STABILITY_KEY = os.getenv("STABLE_API_KEY")

# Stability AI 클라이언트 초기화
stability_api = client.StabilityInference(
    key=STABILITY_KEY,
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)

class T2I_generator:
    @staticmethod
    def generator_image(prompt: str, seed_number: int) -> Image.Image:
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

        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn("Your request activated the API's safety filters. Modify the prompt and try again.")
                elif artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    return img

        return None

def generate_images_from_prompts(prompts: list, seed_number: int, num_images_per_prompt: int = 5):
    for i, prompt in enumerate(prompts):
        for j in range(num_images_per_prompt):
            img = T2I_generator.generator_image(prompt, seed_number + j)
            if img:
                img_path = save_image(img, seed_number + j, i, j)
                print(f"Image for prompt {i} variation {j} saved to {img_path}")
            else:
                print(f"Failed to generate image for prompt {i} variation {j}")

def save_image(img: Image.Image, seed: int, prompt_index: int, variation_index: int) -> str:
    image_dir = Path(__file__).resolve().parent.parent / "static/text_to_image/images/"
    image_dir.mkdir(parents=True, exist_ok=True)
    img_filename = f"prompt_{prompt_index}_variation_{variation_index}_seed_{seed}.png"
    img_path = image_dir / img_filename
    img.save(img_path)
    return str(img_path)

# 프롬프트 목록
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

# 고정 시드 값 설정
fixed_seed = random.randint(0, 2**32-1)
print(f"{fixed_seed}", "is the fixed seed.")

# 각 프롬프트에 대해 이미지 생성
generate_images_from_prompts(prompts, fixed_seed)
