from flask import Flask, request, jsonify
from flask_cors import CORS

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

# 标准化邮箱地址的函数
def normalize_email(email):
    return email.replace('%0d', '').replace('%0a', '').replace('%20', '').strip()

# 注册接口
@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')

    # 标准化邮箱地址
    clean_email = normalize_email(email)

    # 覆盖已有用户的密码
    users[clean_email] = {
        "password": password,
        "car_info": {
            "VIN": "1HGCM82633A654321",  # 默认值
            "owner": "New Owner",
            "status": "Unlocked",
            "location": "Garage"
        }
    }

    print(f"Registered/Updated: {clean_email} with password: {password}")
    return jsonify({"message": f"User {clean_email} registered"}), 201

# 登录接口
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    # 标准化邮箱地址
    clean_email = normalize_email(email)

    user = users.get(clean_email)

    print(f"Attempted login: {clean_email} with password: {password}")

    if user and user['password'] == password:
        return jsonify({
            "message": "Login successful",
            "car_info": user["car_info"]
        }), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

