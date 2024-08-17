from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# 模拟的数据库，用于存储用户信息和车辆信息
users_db = {
    "nissancust:129383573": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "vehicles": {
            "5FNRL6H82NB044273": {
                "make": "Nissan",
                "model": "Altima",
                "year": 2021,
                "mileage": "12000 miles"
            }
        }
    },
    "toyotacust:483920473": {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "vehicles": {
            "4T1BF1FK0HU123456": {
                "make": "Toyota",
                "model": "Camry",
                "year": 2018,
                "mileage": "30000 miles"
            }
        }
    }
}

# 生成对应的 Bearer token
def generate_token(vin):
    return f"BEARER-TOKEN-{vin}"

# 模拟的API接口
@app.route('/api/exchangeToken', methods=['POST'])
def exchange_token():
    data = request.json
    customer_id = data.get('customerId')
    vin = data.get('vin')

    # 新的漏洞条件：customer_id 内容等于他人的 VIN，返回对应的 Bearer token
    for user in users_db.values():
        if customer_id in user["vehicles"]:
            response_data = {
                "access_token": generate_token(customer_id),
                "CV-APIKey": f"CLIENT-ID-{customer_id}",
                "Expires_in": 299,
                "token_type": "Bearer",
                "refresh_token": f"REFRESH-TOKEN-{customer_id}"
            }
            return jsonify(response_data)

    # 正常的检查条件并返回不同的 Bearer token
    if customer_id == "nissancust:129383573" and vin == "5FNRL6H82NB044273":
        response_data = {
            "access_token": "BEARER-NISSAN",
            "CV-APIKey": "CLIENT-ID-NISSAN",
            "Expires_in": 299,
            "token_type": "Bearer",
            "refresh_token": "REFRESH-TOKEN-NISSAN"
        }
        return jsonify(response_data)

    elif customer_id == "toyotacust:483920473" and vin == "4T1BF1FK0HU123456":
        response_data = {
            "access_token": "BEARER-TOYOTA",
            "CV-APIKey": "CLIENT-ID-TOYOTA",
            "Expires_in": 299,
            "token_type": "Bearer",
            "refresh_token": "REFRESH-TOKEN-TOYOTA"
        }
        return jsonify(response_data)

    # 默认的响应内容
    return jsonify({"error": "Invalid request"}), 400

# 模拟的获取用户信息的API接口
@app.route('/api/userProfile', methods=['GET'])
def user_profile():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        # 根据不同的 Bearer token 返回相应的用户信息
        for user_id, user_info in users_db.items():
            for vin, vehicle_info in user_info["vehicles"].items():
                if generate_token(vin) in auth_header:
                    return jsonify(user_info)

    return jsonify({"error": "Unauthorized"}), 401

# Web页面，包含触发API的表单
@app.route('/')
def index():
    return render_template_string('''
    <html>
    <body>
        <h2>Exchange Token API Test</h2>
        <form action="/submit" method="post">
            Customer ID: <input type="text" name="customerId" value="5FNRL6H82NB044273"><br>
            VIN: <input type="text" name="vin" value=""><br>
            <input type="submit" value="Submit">
        </form>
        <br><br>
        <h2>Get User Profile</h2>
        <form action="/getProfile" method="post">
            Bearer Token: <input type="text" name="bearerToken"><br>
            <input type="submit" value="Submit">
        </form>
    </body>
    </html>
    ''')

# 处理表单提交并发送POST请求到API
@app.route('/submit', methods=['POST'])
def submit():
    customer_id = request.form['customerId']
    vin = request.form['vin']

    # 发送请求到API接口
    api_url = "http://localhost:5000/api/exchangeToken"
    headers = {'Content-Type': 'application/json'}
    data = {'customerId': customer_id, 'vin': vin}
    response = requests.post(api_url, json=data, headers=headers)

    return f"API Response: {response.json()}"

# 获取用户配置文件的表单提交处理
@app.route('/getProfile', methods=['POST'])
def get_profile():
    bearer_token = request.form['bearerToken']

    # 使用 Bearer token 访问用户配置文件
    profile_api_url = "http://localhost:5000/api/userProfile"
    profile_headers = {'Authorization': f'Bearer {bearer_token}'}
    profile_response = requests.get(profile_api_url, headers=profile_headers)

    return f"User Profile: {profile_response.json()}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
