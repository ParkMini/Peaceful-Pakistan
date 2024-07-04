from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit, join_room, leave_room
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from flask_cors import CORS
from PIL import Image
import time
import threading
import os
import uuid
from enum import Enum

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # 세션을 위한 시크릿 키 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@100.100.100.2/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app)
CORS(app, supports_credentials=True)

# 이미지 저장 경로 설정
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 사용자 유형 열거형 정의
class UserType(Enum):
    ADMIN = 'admin'
    USER = 'user'
    SELLER = 'seller'

# 사용자 모델 정의
class User(db.Model):
    __tablename__ = 'users'

    idx = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False, unique=True)
    userType = db.Column(db.Enum(UserType), nullable=False)

    def to_dict(self):
        return {
            'idx': self.idx,
            'username': self.username,
            'phone': self.phone,
            'userType': self.userType.value
        }

# 수리점 모델 정의
class RepairShop(db.Model):
    __tablename__ = 'repair_shops'

    idx = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.idx'), nullable=False)
    description = db.Column(db.String, nullable=True)
    phone_number = db.Column(db.String, nullable=False)
    owner_id = db.Column(db.BigInteger, db.ForeignKey('users.idx'), nullable=False)

    reviews = db.relationship('Review', backref='repair_shop', lazy=True)

    def to_dict(self):
        return {
            'idx': self.idx,
            'name': self.name,
            'location': self.location,
            'category_id': self.category_id,
            'description': self.description,
            'phone_number': self.phone_number,
            'owner_id': self.owner_id,
            'reviews': [review.to_dict() for review in self.reviews]
        }

# 카테고리 모델 정의
class Category(db.Model):
    __tablename__ = 'categories'

    idx = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def to_dict(self):
        return {
            'idx': self.idx,
            'name': self.name
        }

# 검색기록 모델 정의
class SearchRecord(db.Model):
    __tablename__ = 'search_records'

    idx = db.Column(db.BigInteger, primary_key=True)
    question = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
    videoUrl = db.Column(db.ARRAY(db.String), nullable=False)
    questionImgUrl = db.Column(db.String, nullable=False)
    purchaseDate = db.Column(db.Integer, nullable=False)
    productName = db.Column(db.String, nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.idx'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.idx'), nullable=False)
    repair_shop_id = db.Column(db.BigInteger, db.ForeignKey('repair_shops.idx'), nullable=True)
    price = db.Column(db.Float, nullable=True)

    def to_dict(self):
        return {
            'idx': self.idx,
            'question': self.question,
            'message': self.message,
            'videoUrl': self.videoUrl,
            'questionImgUrl': self.questionImgUrl,
            'purchaseDate': self.purchaseDate,
            'productName': self.productName,
            'category_id': self.category_id,
            'user_id': self.user_id,
            'repair_shop_id': self.repair_shop_id,
            'price': self.price
        }

# 평점 모델 정의
class Review(db.Model):
    __tablename__ = 'reviews'

    idx = db.Column(db.BigInteger, primary_key=True)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.idx'), nullable=False)
    repair_shop_id = db.Column(db.BigInteger, db.ForeignKey('repair_shops.idx'), nullable=False)
    score = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            'idx': self.idx,
            'content': self.content,
            'user_id': self.user_id,
            'repair_shop_id': self.repair_shop_id,
            'score': self.score
        }

# 견적 모델 정의
class Estimate(db.Model):
    __tablename__ = 'estimates'

    idx = db.Column(db.String, primary_key=True)
    repair_shop_id = db.Column(db.BigInteger, db.ForeignKey('repair_shops.idx'), nullable=False)
    search_record_id = db.Column(db.BigInteger, db.ForeignKey('search_records.idx'), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'idx': self.idx,
            'repair_shop_id': self.repair_shop_id,
            'search_record_id': self.search_record_id,
            'price': self.price
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
        phone=data['phone'],
        userType=UserType(data['userType'])
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

# 로그인 엔드포인트
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(phone=data['phone']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        session['user_id'] = user.idx
        session['username'] = user.username
        session['user_type'] = user.userType.value
        return jsonify({'message': '로그인 성공', 'user': user.to_dict()})
    return jsonify({'message': '로그인 실패'}), 401

# 판매자 등록 엔드포인트
@app.route('/register_seller', methods=['POST'])
def register_seller():
    data = request.get_json()
    user = User.query.filter_by(phone=data['phone']).first()
    if user:
        user.username = data['username']
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user.userType = UserType.SELLER
        db.session.commit()
        return jsonify(user.to_dict()), 200
    return jsonify({'message': '등록 실패'}), 400

# 사용자 조회
@app.route('/users/<int:idx>', methods=['GET'])
def get_user(idx):
    user = User.query.get_or_404(idx)
    return jsonify(user.to_dict())

# 수리점 등록
@app.route('/repair_shops', methods=['POST'])
def create_repair_shop():
    data = request.get_json()
    new_repair_shop = RepairShop(
        name=data['name'],
        location=data['location'],
        category_id=data['category_id'],
        description=data.get('description', ''),
        phone_number=data['phone_number'],
        owner_id=data['owner_id']
    )
    db.session.add(new_repair_shop)
    db.session.commit()
    return jsonify(new_repair_shop.to_dict()), 201

# 카테고리 등록
@app.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    new_category = Category(name=data['name'])
    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.to_dict()), 201

# 카테고리에 따른 수리점 목록 조회
@app.route('/categories/<int:category_id>/repair_shops', methods=['GET'])
def get_repair_shops_by_category(category_id):
    repair_shops = RepairShop.query.filter_by(category_id=category_id).all()
    return jsonify([repair_shop.to_dict() for repair_shop in repair_shops])

# 검색기록 생성 및 AI 처리
@app.route('/search_records', methods=['POST'])
def create_search_record():
    data = request.form
    user_id = data.get('user_id')
    product_name = data.get('product_name')
    purchase_date = int(data.get('purchase_date'))
    category_id = int(data.get('category_id'))
    question = data.get('question')
    repair_shop_id = int(data.get('repair_shop_id'))
    price = float(data.get('price'))

    # 이미지 파일 처리
    image_urls = []
    files = request.files.getlist('images')
    for file in files:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        image_urls.append(file_path)

    # AI 질문 생성
    ai_question = f"{product_name} 제품을 {purchase_date}년 전에 구매했는데, {question} 문제가 있어. 어떻게 해결하면 돼?"

    # AI 응답 처리
    youtube_links, response_message = send_message_and_get_response(ai_question)

    # 검색 기록 저장
    new_search_record = SearchRecord(
        question=question,
        message=response_message,
        videoUrl=youtube_links,
        questionImgUrl=','.join(image_urls),
        purchaseDate=purchase_date,
        productName=product_name,
        category_id=category_id,
        user_id=user_id,
        repair_shop_id=repair_shop_id,
        price=price
    )
    db.session.add(new_search_record)
    db.session.commit()

    return jsonify(new_search_record.to_dict()), 201

# 평점 등록
@app.route('/reviews', methods=['POST'])
def create_review():
    data = request.get_json()
    new_review = Review(
        content=data['content'],
        user_id=data['user_id'],
        repair_shop_id=data['repair_shop_id'],
        score=data['score']
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify(new_review.to_dict()), 201

# 수리점 조회 시 평점 포함
@app.route('/repair_shops/<int:idx>', methods=['GET'])
def get_repair_shop(idx):
    repair_shop = RepairShop.query.get_or_404(idx)
    return jsonify(repair_shop.to_dict())

# 사용자의 모든 검색 기록 조회
@app.route('/search_records', methods=['GET'])
def get_all_search_records():
    user_id = request.args.get('user_id')
    search_records = SearchRecord.query.filter_by(user_id=user_id).all()
    return jsonify([record.to_dict() for record in search_records])

# 특정 검색 기록 조회
@app.route('/search_records/<int:idx>', methods=['GET'])
def get_search_record(idx):
    search_record = SearchRecord.query.get_or_404(idx)
    return jsonify(search_record.to_dict())

# 견적 생성
@app.route('/estimates', methods=['POST'])
def create_estimate():
    data = request.get_json()
    new_estimate = Estimate(
        idx=str(uuid.uuid4()),
        repair_shop_id=data['repair_shop_id'],
        search_record_id=data['search_record_id'],
        price=data['price']
    )
    db.session.add(new_estimate)
    db.session.commit()

    # 소켓으로 데이터 전송
    room = data['search_record_id']
    estimate_data = {
        "name": new_estimate.repair_shop.name,
        "location": new_estimate.repair_shop.location,
        "idx": new_estimate.idx,
        "price": new_estimate.price
    }
    socketio.emit('new_estimate', estimate_data, room=room)
    
    return jsonify(new_estimate.to_dict()), 201

# 소켓 엔드포인트
@socketio.on('join')
def on_join(data):
    search_record_id = data['search_record_id']
    join_room(search_record_id)
    emit('message', {'msg': f'Joined room: {search_record_id}'})

@socketio.on('leave')
def on_leave(data):
    search_record_id = data['search_record_id']
    leave_room(search_record_id)
    emit('message', {'msg': f'Left room: {search_record_id}'})

# 견적 선택
@app.route('/select_estimate', methods=['POST'])
def select_estimate():
    data = request.get_json()
    search_record_id = data['search_record_id']
    estimate = Estimate.query.filter_by(idx=data['estimate_id']).first_or_404()

    search_record = SearchRecord.query.get_or_404(search_record_id)
    search_record.repair_shop_id = estimate.repair_shop_id
    search_record.price = estimate.price
    db.session.commit()

    # 소켓 서버 종료
    socketio.emit('close_room', {'msg': 'Room closed'}, room=search_record_id)
    leave_room(search_record_id)

    return jsonify(search_record.to_dict()), 200

def run_flask():
    socketio.run(app, host='0.0.0.0', port=5000)

# Flask 서버를 별도의 스레드에서 실행
threading.Thread(target=run_flask).start()
