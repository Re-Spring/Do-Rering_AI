# 여기가 large_language_model prompt 처리하는 모듈 파트

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import httpx

class Large_language_model_module:
    def __init__(self, api_key):
        self.api_key = api_key

    async def generate_story(self, data):
        # 클라이언트로부터 전송받은 JSON 데이터를 파싱합니다.

        keys_to_delete = []  # 삭제할 키를 저장할 빈 리스트 생성
        data = await data.json()

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
                    "role": "system",
"content":"""
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
There are important things to keep for that goal.
While working on it, please refer to "important things" to create a fairy tale.

## important things
-` If the value of the data entered by the user is "no request data", ignore the parameter.
- Make sure that everything is reflected except for the ignored parameters.
- Please enter only the value of the title parameter entered by the user in the first paragraph.
- Among the parameters entered by the user, the number of paragraphs must be observed, and the title must be
Do not include in the number of paragraphs.
- The generated fairy tale should be printed in Korean.
- In the process of creating fairy tales, please do not create any contents other than fairy tales.
""",
"role": "user",
"content": f"""
# Create a fairy tale based on the elements of the fairy tale.

## main character : {character}
## keyword : {keyword}
## title : {title}
## lessons : {lesson}
## genre : {genre}
## paragraphs : {page}

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

    async def summary_story(self, english_prompts):

        print("summary_story 들어옴")
        print("engilsh_prompts : ", english_prompts)


        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4-turbo-preview",
            "messages" : [
                {
                    "role": "system", "content": """ 
                    # Role
                    - Your role is to summarize the contents of the fairy tale you received.
                    
                    # Output Format
                    {
                        summary : {summary}
                    }
                    
                    # Task
                    - Please summarize according to the conditions given
                                        
                    # Condition 1
                    - Please make sure that the number of tokens in the summary value does not exceed 100..
                    
                    # Condition 2
                    - When summarizing the content, please be aware that the content was only entered in the middle and summarize it.
                    
                    # Condition 3
                    - Summarize the content briefly, and at the end of the day, finish it in a question format curious to see what the latter part will look like.
                    
                    # Condition 4
                    - Please make sure that the title does not come up when you print it out as the result value.
                    """,
                    "role": "user", "content": f"""
                    - Please summarize the contents of the fairy tale and return it to Korean.
                    - Please don't use formal phrases such as "summary of fairy tales" when printing.
                    
                    # fairytale : {english_prompts}
                    """
                }
            ],
            "max_tokens": 3000,
            "temperature": 1,
            "n": 1,
        }

        timeout = httpx.Timeout(300.0, connect=300.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post('https://api.openai.com/v1/chat/completions', json=payload, headers=headers)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()
            choice = result['choices'][0]

            if 'message' in choice and 'content' in choice['message']:
                summary_text = choice['message']['content']

            print(summary_text)

            if summary_text:
                return JSONResponse(content=summary_text)
            else:
                raise HTTPException(status_code=500, detail="Story generation failed.")
