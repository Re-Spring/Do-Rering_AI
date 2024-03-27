import os
from io import BytesIO

import openai
from fastapi import FastAPI
from dotenv import load_dotenv
import asyncio
from pathlib import Path
import httpx  # httpx를 임포트합니다.
from datetime import datetime
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import textwrap

class Text_to_image():

    def __init__(self, api_key, image_font_path, image_path, character_image_path):
        self.api_key = api_key
        self.image_font_path = image_font_path
        self.image_path = image_path
        self.character_image_path = character_image_path

    async def character_image(self, title, summary):
        response = openai.images.generate(
            model="dall-e-3",
            prompt=f"""
                                # Role
                                ## You are a painter who produces pictures of fairy tales.

                                # Task
                                ## Draw the main character by referring to the contents of the fairy tale you entered.
                                ## Focus on the main character and draw a picture of the main character
                                ## Prevent text from being created in the image when creating the image
                                ## Draw one character

                                # title : {title}
                                # story : {summary}
                            """,
            size="1792x1024",
            quality="standard",
            n=1,
        )

        character_image_url = response.data[0].url
        now = datetime.now()
        now = now.strftime("%Y%m%d%H%M%S")
        char_name = f"{title}_{now}.png"
        character_image_path = os.path.join(self.character_image_path, char_name)
        async with httpx.AsyncClient() as client:
            response = await client.get(character_image_url)
        character_bytes = BytesIO(response.content)
        character = Image.open(character_bytes)
        character = remove(character)
        character.save(character_image_path)

        return character_image_path

    # character_image에서 생성한 img_url을 받아서 생성
    async def title_image(self, title, summary, user_id, main_character_path):
        response = openai.images.generate(
            model="dall-e-3",
            prompt=f"""
            # Role
            ## You are a designer tasked with creating a cover for a fairy tale book.

            # Task
            ## Don't break the terms of "#conditions" and create an image

            # Conditions
            1.  Make the main character of "# Main Character Image" the same
            2. Create a picture according to the story
            3. Create a picture that corresponds to one scene in the fairy tale.
            4. Never include letters in the picture

            # Title: {title}

            # Summary:
            {summary}

            # Main Character Image:
            ![Character Image]({main_character_path})

            """,
            size="1792x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        file_name = f"{title}/{title}.png"
        save_file_path = os.path.join(self.image_path, user_id, file_name)
        file_path = Path(os.path.join(self.image_path, user_id, file_name))

        await self.save_image(image_url=image_url, file_path=file_path, story=title)

        return save_file_path

    async def story_image(self, title, story, user_id, main_character_url, page):
        response = openai.images.generate(
            model="dall-e-3",
            prompt=f"""# Role
            ## You are a designer tasked with creating images for a fairy tale book.

            # Task
            ## Create captivating images that depict scenes from the story below.

            # Conditions
            1. The main character must be consistent with the provided main character image: ![Main Character]({main_character_url}).
            2. The art style of the images should match the cover previously created.
            3. The images should reflect the situations described in the provided story.
            4. Draw a picture that corresponds to one scene in the fairy tale.
            5. Never include letters in the picture

            # Main Character:
            ![Main Character]({main_character_url})

            # Art Style Reference:
            ![Art Style]({main_character_url})

            # Story:
            {story}

            # Korean Font Path:
            {self.image_font_path}
        """,
            size="1792x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        file_name = f"{title}/{title}_{page}.png"
        save_file_path = os.path.join(self.image_path, user_id, file_name)
        file_path = Path(os.path.join(self.image_path, user_id, file_name))

        await self.save_image(image_url=image_url, file_path=file_path, story=story)

        return save_file_path

    async def save_image(self, image_url, file_path, story):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code == 200:
                img_bytes = BytesIO(response.content)
                img = Image.open(img_bytes)
                img = self.add_text(img=img, text=story)
                img.save(file_path)
                print(f"Image saved to {file_path}")
            else:
                print("Failed to download the image")

    def add_text(self, img: Image.Image, text, position: tuple = (10, 10), font_size: int = 26, padding: int = 10):
        draw = ImageDraw.Draw(img, "RGBA")
        font = ImageFont.truetype(self.image_font_path, font_size)
        lines = textwrap.wrap(text, width=80)

        # 텍스트의 전체 높이 및 최대 너비를 계산합니다.
        max_width = 0
        total_height = 0
        line_heights = []
        for line in lines:
            text_width, text_height = draw.textsize(line, font=font)
            max_width = max(max_width, text_width)
            total_height += text_height + 5  # 줄 간격
            line_heights.append(text_height + 5)

        total_height -= 5  # 마지막 줄 간격 제거

        # 박스의 위치와 크기를 계산합니다.
        box_x0 = position[0] - padding
        box_y0 = position[1] - padding
        box_x1 = position[0] + max_width + padding
        box_y1 = position[1] + total_height + padding

        # 투명도가 있는 밝은 회색 배경의 박스를 그립니다.
        draw.rectangle([box_x0, box_y0, box_x1, box_y1], fill=(192, 192, 192, 77))  # RGBA

        # 각 줄의 텍스트를 그립니다.
        y_position = position[1]
        for i, line in enumerate(lines):
            draw.text((position[0], y_position), line, font=font, fill=(0, 0, 0))
            y_position += line_heights[i]

        return img

    async def generate_entire_story_image(self, title, user_id, summary, no_title_ko_pmt, count):
        print("generate 들어옴")
        image_paths = []
        # 먼저 메인 캐릭터 만들기
        main_character_url = await self.character_image(title=title, summary=summary)
        print("메인 캐릭터 만들었음")

        # 메인 캐릭터 url로 동화 표지 만들기
        title_path = await self.title_image(title=title, summary=summary, user_id=user_id, main_character_path=main_character_url)
        print("표지 만듦")
        # 동화 표지로 나머지
        for page in range(0, count-1):
            image_path = await self.story_image(title=title, story=no_title_ko_pmt[page], user_id=user_id, main_character_url=title_path, page=page+1)

            image_paths.append(image_path)
            print(f"{page}page 생성완료")

        return title_path, image_paths