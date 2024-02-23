from flask import Flask, request, render_template, send_from_directory, url_for
import requests
import time
import os

app = Flask(__name__)

AUDIO_FOLDER = os.path.join(app.static_folder, 'API/audio_files')
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        API_TOKEN = '__pltB7u3B5B8RQutg85jDrzkiH9oVbpyaNRnigJP6XAm'

        HEADERS = {'Authorization': f'Bearer {API_TOKEN}'}

        actor_id = "622964d6255364be41659078"
        data = {
            'text': text,
            'lang': 'auto',
            "tempo": 1,
            "pitch": 1,
            'actor_id': actor_id,
            'xapi_hd': True,
            'model_version': 'latest'
        }
        response = requests.post('https://typecast.ai/api/speak', headers=HEADERS, json=data)
        if response.status_code == 200:
            speak_url = response.json()['result']['speak_v2_url']
            
            # 폴링 로직 추가
            for _ in range(60):  # 최대 1분간 대기
                r = requests.get(speak_url, headers=HEADERS)
                if r.status_code == 200 and r.json()['result']['status'] == 'done':
                    audio_url = r.json()['result']['audio_download_url']
                    filename = f"{time.strftime('%Y%m%d-%H%M%S')}.wav"
                    filepath = os.path.join(AUDIO_FOLDER, filename)
                    
                    # 음성 파일 다운로드 및 저장
                    audio_response = requests.get(audio_url)
                    with open(filepath, 'wb') as f:
                        f.write(audio_response.content)
                    
                    # 생성된 음성 파일의 URL을 생성
                    audio_url = url_for('static', filename=f'API/audio_files/{filename}')
                    return render_template('API/index.html', audio_file=audio_url, filename=filename)
                time.sleep(1)  # 1초 대기
            return "음성 파일 생성에 시간이 너무 오래 걸립니다."

        else:
            return f"Error: {response.text}"

    return render_template('API/index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(AUDIO_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
