from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# 크롬 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument("--start-fullscreen")
driver = webdriver.Chrome(options=options)

# 1. 웹사이트 접속
driver.get('https://sso.wrtn.ai/')
time.sleep(20)  # 페이지 로드 대기

while True:
    # 사용자로부터 입력 받기
    text = input("입력할 텍스트를 입력하세요 (종료하려면 'exit' 입력): ")
    if text.lower() == 'exit':
        break

    # 텍스트 입력 및 엔터키 입력
    text_area = driver.find_element(By.CSS_SELECTOR, '#chat-content > div.css-stgup8 > div > div.css-i0s7nd > div > div.css-butkt4 > div.css-18t4f18 > div > div.css-1o86z8t > div.css-1bc0574 > textarea')
    text_area.send_keys(text)
    text_area.send_keys(Keys.ENTER)

    # 최소 10초 대기
    time.sleep(10)

    # 유튜브 영상 링크 가져오기
    youtube_links = driver.execute_script(
        "return Array.from(document.querySelectorAll('#chat-content > div.css-stgup8 > div > div.css-1g4yje1 > div.css-jq48ft > div > div > div > div > div.css-0 > div:last-child > div > div > div > div:nth-child(2) > div:nth-child(2) > div > div > div:nth-child(2) > div > div iframe')).map(elem => elem.src);")
    for link in youtube_links:
        print("YouTube 링크:", link)

    # AI 생성 결과 텍스트 가져오기
    ai_result = driver.execute_script(
        "return document.querySelector('#chat-content > div.css-stgup8 > div > div.css-1g4yje1 > div.css-jq48ft > div > div > div > div > div.css-0 > div:last-child > div > div > div > div:nth-child(3)').innerText;")
    print("AI 생성 결과:", ai_result)

# 필요한 작업이 끝난 후 브라우저 닫기
driver.quit()
