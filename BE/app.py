from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import threading
from enum import Enum

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # 세션을 위한 시크릿 키 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@100.100.100.2/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# 사용자 유형 열거형 정의
class UserType(Enum):
    ADMIN = 'admin'
    USER = 'user'
    SELLER = 'seller'

# 사용자 모델 정의
class User(db.Model):
    __tablename__ = 'users'

    idx = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    userType = db.Column(db.Enum(UserType), nullable=False)

    def to_dict(self):
        return {
            'idx': self.idx,
            'username': self.username,
            'userType': self.userType.value
        }

# 데이터베이스 초기화
with app.app_context():
    db.create_all()

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

# 회원가입 엔드포인트
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        userType=UserType(data['userType'])
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

# 로그인 엔드포인트
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        session['user_id'] = user.idx
        session['username'] = user.username
        session['user_type'] = user.userType.value
        return jsonify({'message': '로그인 성공', 'user': user.to_dict()})
    return jsonify({'message': '로그인 실패'}), 401

# 사용자 생성
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(
        username=data['username'],
        password=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
        userType=UserType(data['userType'])
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

# 사용자 조회
@app.route('/users/<int:idx>', methods=['GET'])
def get_user(idx):
    user = User.query.get_or_404(idx)
    return jsonify(user.to_dict())

# 사용자 업데이트
@app.route('/users/<int:idx>', methods=['PUT'])
def update_user(idx):
    data = request.get_json()
    user = User.query.get_or_404(idx)
    user.username = data.get('username', user.username)
    if 'password' in data:
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user.userType = UserType(data.get('userType', user.userType.value))
    db.session.commit()
    return jsonify(user.to_dict())

# 사용자 삭제
@app.route('/users/<int:idx>', methods=['DELETE'])
def delete_user(idx):
    user = User.query.get_or_404(idx)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# AI 엔드포인트
@app.route('/ai', methods=['POST'])
def ai():
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    youtube_links, response_message = send_message_and_get_response(message)
    return jsonify({'youtube_links': youtube_links, 'message': response_message})

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Flask 서버를 별도의 스레드에서 실행
threading.Thread(target=run_flask).start()
