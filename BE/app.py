from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import threading

app = Flask(__name__)

# 크롬 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument("--start-fullscreen")
driver = webdriver.Chrome(options=options)

# 1. 웹사이트 접속
driver.get('https://sso.wrtn.ai/')
time.sleep(20)  # 페이지 로드 대기

def send_message_and_get_response(text):
    # 텍스트 입력 및 엔터키 입력
    text_area = driver.find_element(By.CSS_SELECTOR, '#chat-content > div.css-stgup8 > div > div.css-i0s7nd > div > div.css-butkt4 > div.css-18t4f18 > div > div.css-1o86z8t > div.css-1bc0574 > textarea')
    text_area.send_keys(text)
    text_area.send_keys(Keys.ENTER)

    # 최소 10초 대기
    time.sleep(10)

    # 유튜브 영상 링크 가져오기
    youtube_links = driver.execute_script(
        "return Array.from(document.querySelectorAll('#chat-content > div.css-stgup8 > div > div.css-1g4yje1 > div.css-jq48ft > div > div > div > div > div.css-0 > div:last-child > div > div > div > div:nth-child(2) > div:nth-child(2) > div > div > div:nth-child(2) > div > div iframe')).map(elem => elem.src);")

    # AI 생성 결과 텍스트 가져오기
    ai_result = driver.execute_script(
        "return document.querySelector('#chat-content > div.css-stgup8 > div > div.css-1g4yje1 > div.css-jq48ft > div > div > div > div > div.css-0 > div:last-child > div > div > div > div:nth-child(3)').innerText;")

    return youtube_links, ai_result

@app.route('/ai', methods=['POST'])
def ai():
    data = request.get_json()
    message = data.get('message')
    message = message.replace("\n\n", "\n")
    
    # 메시지 필터링
    message = message.replace(" [res_idx]", "")
    message = message.replace("[res_idx]", "")
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    youtube_links, response_message = send_message_and_get_response(message)
    
    for i in range(0, len(youtube_links)):
        youtube_links[i] = youtube_links[i].split("?")[0]
    
    return jsonify({'youtube_links': youtube_links, 'message': response_message})

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Flask 서버를 별도의 스레드에서 실행
threading.Thread(target=run_flask).start()
