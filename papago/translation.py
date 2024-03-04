import requests
import json

# 1. APP 등록 - Access token
CLIENT_ID, CLIENT_SECRET = '29Pxb__M4MwWUPBgtAbz','t83ggTaMjr'

def en_translate(text) :

    # 2. Request (en 외의 언어로 번역도 가능)
    # text 한글자에 1씩 10000개까지 가능
    url = 'https://openapi.naver.com/v1/papago/n2mt'
    headers = {
        'Content-Type': 'application/json',
        'X-Naver-Client-Id': CLIENT_ID,
        'X-Naver-Client-Secret': CLIENT_SECRET
    }
    data = {'source': 'ko', 'target': 'en', 'text': text}

    # post 방식으로 서버쪽으로 요청
    response = requests.post(url, json.dumps(data), headers=headers)
    # print(response)  # 정상 응답인지 확인
    
    # 3. response(en) -> en_txt
    # print(response.text)  # 응답 출력 - 내용이 dictionary인 str
    
    # json() 후 key 값을 사용하여 원하는 텍스트 접근
    en_text = response.json()['message']['result']['translatedText']
    print(en_text)
    return en_text

def kr_translate(text) :

    # 2. Request (en 외의 언어로 번역도 가능)
    # text 한글자에 1씩 10000개까지 가능
    url = 'https://openapi.naver.com/v1/papago/n2mt'
    headers = {
        'Content-Type': 'application/json',
        'X-Naver-Client-Id': CLIENT_ID,
        'X-Naver-Client-Secret': CLIENT_SECRET
    }
    data = {'source': 'en', 'target': 'ko', 'text': text}

    # post 방식으로 서버쪽으로 요청
    response = requests.post(url, json.dumps(data), headers=headers)
    # print(response)  # 정상 응답인지 확인
    
    # 3. response(en) -> en_txt
    # print(response.text)  # 응답 출력 - 내용이 dictionary인 str
    
    # json() 후 key 값을 사용하여 원하는 텍스트 접근
    ko_text = response.json()['message']['result']['translatedText']
    print(ko_text)
    return ko_text