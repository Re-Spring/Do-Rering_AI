# 여기가 large_language_model prompt 처리하는 모듈 파트

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import httpx



class LLM_module:
    def __init__(self, api_key):
        self.api_key = api_key

    async def generate_story(self, request: Request):
        # 클라이언트로부터 전송받은 JSON 데이터를 파싱합니다.
        data = await request.json()

        keys_to_delete = []  # 삭제할 키를 저장할 빈 리스트 생성

        for key, value in data.items():  # data.items()로 키-값 쌍들을 반복
            if value == "":  # 값이 빈 문자열인 경우
                keys_to_delete.append(key)  # 삭제할 키를 리스트에 추가

        for key in keys_to_delete:  # 삭제할 키들을 반복하면서
            del data[key]  # 딕셔너리에서 해당 키-값 쌍을 제거

        title = data.get("title", "no request data")
        character = data.get("character", "no request data")
        genre = data.get("genre", "no request data")
        keyword = data.get("keyword", "no request data")
        lesson = data.get("lesson", "no request data")
        page = data.get("page", "no request data")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 프롬프트 및 API 요청에 사용할 payload 설정
        payload = {
            "model": "gpt-4-turbo-preview",
            "messages": [
                {
                    "role": "system", "content":"""
# Role
You are a fairy tale writer who creates fairy tales professionally and creatively.

# Audience
- This is for Python developers who want to develop an automatic fairy tale generator.
- Do not write any content other than the json string, because the resulting json string must be used directly in the script.


# Output Format
{
"title" : "{title}",
"story" : "{story}"
}

# Task
The ultimate goal is to generate fairy tales by referring to the data sent by the user.
To do that, I'll think about each step.
Please refer to "# Fairytale Attribute" for the six elements of fairy tales.

## Step 1
In the process of writing fairy tales, we will refer to six elements of fairy tales.
If there is a value of no request data among the six elements, please proceed to Step 2,
If you don't have one, please go to Step 3.

## Step 2
In the process of generating the fairy tale, please move to Step 3 on the condition that you do not think of the six elements of the fairy tale with the value of no request data.

## Step 3
- In this step, we will generate values for elements with values that are no request data based on the priorities of the elements of fairy tales.
- First of all, the higher the priority, the higher the elements of assimilation with the value of no request data will be created first.
- Create an element of fairy tale with the value of no request data by referring to the elements of fairy tale in order of priority, not the value of no request data.
- However, for elements created in order in this case, the reference should be accompanied when the following elements are created.

## Step 4
- In this step, we will create a fairy tale.
- All six elements of the fairy tale completed in Step 4 are referred to in priority.
- Create a fairy tale based on the elements of the fairy tale you referenced.
- However, the Number of paragraps in fairy tail, which determines the number of pages in a fairy tale, should never be different from the number of pages.


# Fairytale Attribute
## The main character of the fairy tale
- It is an element that means the protagonist of a fairy tale.
- It has the highest priority among the elements of fairy tales.
- This element must be in the first line.

## Keyword of fairy tale
- It is an element that means the keyword that the user really wants to use.
- It has the second priority among the elements of fairy tales.

## The title of the fairy tale
- It's an element that means the title of a fairy tale.
- It has the third priority among the elements of fairy tales.

## Lessons from fairy tales
- It is an element that means the lessons that can be learned from the fairy tale.
- It has the fourth priority among the elements of fairy tales.

## Genre of fairy tales
- It is an element that means the genre of the fairy tale.
- It has the fifth priority among the elements of fairy tales.

## Number of paragraphs in fairy tale
- The element that means the number of pages in the fairy tale.
- The corresponding element specifies the number of paragraphs excluding the title when creating the fairy tale.
- It has the last priority among the elements of the fairy tale.
- The priority is low, but it is a factor that must be followed.

# policy
- The resulting fairy tale should be in Korean.
- Please fill out the document type in the Json Format form below.
- Do not write any content other than the json string, because the resulting json string must be used directly in the script.
- Do not write unnecessary explanations, instructions, or answers, but only print out the contents related to fairy tales.
- When displaying a title, you should only display the title
- Don't use words that tell you the structure or the end.
    ex) The end, title : , ...
- The number of pages generated by the Number of paragraps in fair tail property must be observed.
""",
            "role": "user", "content": f"""# Create a fairy tale based on the elements of the fairy tale.

                ## The main character of the fairy tale : {character}
                ## Keyword of fairy tale : {keyword}
                ## The title of the fairy tale : {title}
                ## Lessons from fairy tale : {lesson}
                ## Genre of fairy tales : {genre}
                ## Number of paragraphs in fairy tale : {page}

                # request
                ## Please print out the fairy tale in Korean           
                ## Please print out the title on the first line
"""
                }
            ],
            "max_tokens": 3000,
            "temperature": 1,
            "n": 1,
        }

        timeout = httpx.Timeout(600.0, connect=600.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post('https://api.openai.com/v1/chat/completions', json=payload, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()
            choice = result['choices'][0]
            
            if 'message' in choice and 'content' in choice['message']:
                story_text = choice['message']['content'].strip().replace("*", "").replace("#", "").replace("제목:", "").strip()
                paragraphs = story_text.split("\n\n")
                story_dict = {f"paragraph{i}": para for i, para in enumerate(paragraphs)}
                # return story_dict
                return JSONResponse(content=story_dict)
            else:
                raise HTTPException(status_code=500, detail="Story generation failed.")


