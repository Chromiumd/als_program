from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求

# 模拟数据库
users = {
    "victim@gmail.com": {
        "password": "securepassword",
        "car_info": {
            "VIN": "1HGCM82633A123456",
            "owner": "Victim Name",
            "status": "Locked",
            "location": "Unknown"
        }
    },
    "example1@gmail.com": {
        "password": "examplepass1",
        "car_info": {
            "VIN": "2HGCM82633A654321",
            "owner": "Example User 1",
            "status": "Unlocked",
            "location": "Driveway"
        }
    },
    "example2@gmail.com": {
        "password": "examplepass2",
        "car_info": {
            "VIN": "3HGCM82633A987654",
            "owner": "Example User 2",
            "status": "Locked",
            "location": "Work"
        }
    }
}

# 注册接口，不处理控制字符
@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')

    # 注册新用户（不处理字符，可能会导致伪装邮箱）
    if email in users:
        return jsonify({"message": "User already exists"}), 400

    # 注册新用户
    users[email] = {
        "password": password,
        "car_info": {
            "VIN": "1HGCM82633A654321",  # 默认值
            "owner": "New Owner",
            "status": "Unlocked",
            "location": "Garage"
        }
    }

    return jsonify({"message": "Registration successful"}), 201

# 登录接口
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    # 登录时处理控制字符，将%0d视为空格
    clean_email = email.replace('%0d', '')

    user = users.get(clean_email)
    if user and user['password'] == password:
        return jsonify({
            "message": "Login successful",
            "car_info": user["car_info"]
        }), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

