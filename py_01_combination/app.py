from flask import Flask, request, jsonify, render_template_string, render_template, session, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
import pyotp
from flask_cors import CORS
import requests

app1 = Flask(__name__)

# 模拟的数据库，用于存储用户信息和车辆信息
app1_users = {
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
@app1.route('/api/exchangeToken', methods=['POST'])
def exchange_token():
    data = request.json
    customer_id = data.get('customerId')
    vin = data.get('vin')

    # 新的漏洞条件：customer_id 内容等于他人的 VIN，返回对应的 Bearer token
    for user in app1_users.values():
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
@app1.route('/api/userProfile', methods=['GET'])
def user_profile():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        # 根据不同的 Bearer token 返回相应的用户信息
        for user_id, user_info in app1_users.items():
            for vin, vehicle_info in user_info["vehicles"].items():
                if generate_token(vin) in auth_header:
                    return jsonify(user_info)

    return jsonify({"error": "Unauthorized"}), 401

# Web页面，包含触发API的表单
@app1.route('/')
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

import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
@app1.route('/submit', methods=['POST'])
def submit():
    # 记录登录日志
    logging.info('Login attempt started')

    # 尝试获取表单数据
    try:
        customer_id = request.form['customerId']
        vin = request.form['vin']
    except KeyError as e:
        logging.error('Missing data in login attempt: %s', e)
        return "Missing data", 400

    # 发送请求到API接口
    api_url = "http://localhost:5000/api/exchangeToken"
    headers = {'Content-Type': 'application/json'}
    data = {'customerId': customer_id, 'vin': vin}
    response = requests.post(api_url, json=data, headers=headers)

    # 记录API请求的日志
    logging.info('API request made to %s with data %s', api_url, data)

    # 检查响应状态
    if response.status_code == 200:
        logging.info('API response received with status %d', response.status_code)
    else:
        logging.warning('API response received with status %d', response.status_code)

    # 返回API的响应
    return f"API Response: {response.json()}"

# 获取用户配置文件的表单提交处理
@app1.route('/getProfile', methods=['POST'])
def get_profile():
    bearer_token = request.form['bearerToken']

    # 使用 Bearer token 访问用户配置文件
    profile_api_url = "http://localhost:5000/api/userProfile"
    profile_headers = {'Authorization': f'Bearer {bearer_token}'}
    profile_response = requests.get(profile_api_url, headers=profile_headers)

    return f"User Profile: {profile_response.json()}"


app2 = Flask(__name__)
CORS(app2)  # 允许所有来源的跨域请求

# 模拟数据库
app2_users = {
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
@app2.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')

    # 标准化邮箱地址
    clean_email = normalize_email(email)

    # 覆盖已有用户的密码
    app2_users[clean_email] = {
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
@app2.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    # 标准化邮箱地址
    clean_email = normalize_email(email)

    user = app2_users.get(clean_email)

    print(f"Attempted login: {clean_email} with password: {password}")

    if user and user['password'] == password:
        return jsonify({
            "message": "Login successful",
            "car_info": user["car_info"]
        }), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

app3 = Flask(__name__)
app3.config['SECRET_KEY'] = 'your_secret_key'
app3.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app3)

# Simulated user data
app3_users = {
    'user1@toyota.com': {'password': 'password1', 'info': 'User 1 Information'},
    'user2@toyota.com': {'password': 'password2', 'info': 'User 2 Information'},
    'user3@toyota.com': {'password': 'password3', 'info': 'User 3 Information'},
    'user4@toyota.com': {'password': 'password4', 'info': 'User 4 Information'},
    'user5@toyota.com': {'password': 'password5', 'info': 'User 5 Information'}
}

@app3.route('/')
def index():
    return render_template('main_login.html')

@app3.route('/toyota_login')
def toyota_login():
    return render_template('toyota_login.html')

@app3.route('/login', methods=['POST'])
def login_api():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Check if the username and password are correct
    user = app3_users.get(email)
    if user and user['password'] == password:
        access_token = create_access_token(identity=email)
        session['token'] = access_token  # Store token in session
        session['email'] = email         # Store user identity in session
        return redirect(url_for('dashboard'))
    
    # If the credentials are incorrect, attempt to verify JWT
    try:
        verify_jwt_in_request()
        email = get_jwt_identity()
        session['token'] = request.headers.get('Authorization').split()[1]  # Use existing JWT
        session['email'] = email
        return redirect(url_for('dashboard'))
    except Exception:
        return '登录失败', 401

@app3.route('/dashboard')
def dashboard():
    # Check if the user is logged in via session
    if 'email' in session:
        toyota_users = list(app3_users.keys())
        return render_template('dashboard.html', toyota_users=toyota_users)
    
    # If not logged in, show a simplified dashboard with options only
    toyota_users = []  # No user-specific information
    return render_template('dashboard_simplified.html', toyota_users=toyota_users)

@app3.route('/survey/<email>')
def survey(email):
    if 'email' not in session:
        return redirect(url_for('index'))
    
    user_info = app3_users.get(email, {}).get('info', 'No information available')
    return render_template('survey.html', user_info=user_info)

@app3.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('email', None)
    response = redirect(url_for('index'))
    unset_jwt_cookies(response)
    return response

@app3.route('/generate_jwt', methods=['POST'])
def generate_jwt():
    email = request.form.get('email')
    if email in app3_users:
        token = create_access_token(identity=email)
        return token
    return '用户不存在', 404

@app3.before_request
def require_login():
    endpoint = request.endpoint
    if endpoint in ['survey', 'dashboard'] and 'email' not in session:
        # Allow access to a simplified dashboard but enforce login for other routes
        if endpoint == 'dashboard':
            return None
        return redirect(url_for('index'))

app4 = Flask(__name__)
CORS(app4)  # 允许跨域请求

# 模拟的数据库
app4_users = {
    "john.doe": {
        "email": "john.doe@example.com",
        "password": "securepassword123",
        "totp_secret": "JBSWY3DPEHPK3PXP",
        "vin": "1HGCM82633A123456"
    },
    "jane.smith": {
        "email": "jane.smith@example.com",
        "password": "anotherpassword456",
        "totp_secret": "KVKFKRCPNZQUYMLX",
        "vin": "1HGCM82633A654321"
    }
}

@app4.route('/')
def home():
    return render_template('login.html')  # 修改首页为登录页面

@app4.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = app4_users.get(username)
        if user and user['password'] == password:
            # 登录成功，重定向到个人信息页面
            return redirect(url_for('user_info', username=username))
        else:
            # 登录失败，返回错误信息
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app4.route('/user_info.html')
def user_info():
    username = request.args.get('username', '')
    user = app4_users.get(username)
    if user:
        return render_template('user_info.html', user=user)
    else:
        return render_template('user_info.html', error="User not found")

@app4.route('/totp_request.html')
def totp_request():
    username = request.args.get('username', '')
    user = app4_users.get(username)
    if user:
        return render_template('totp_request.html', username=username)
    else:
        return render_template('totp_request.html', username=None)

@app4.route('/totp.html')
def totp():
    username = request.args.get('username', '')
    user = app4_users.get(username)
    if user:
        totp = pyotp.TOTP(user['totp_secret'], interval=300)  # Set interval to 300 seconds (5 minutes)
        totp_code = totp.now()  # Generate TOTP code
        return render_template('totp.html', totp_code=totp_code)
    else:
        return render_template('totp.html', totp_code=None)

@app4.route('/reset_password.html', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.json.get('username')
        user = app4_users.get(username)
        if not user:
            return render_template('reset_password.html', error="User not found")

        totp_code = request.json.get('totp_code')
        totp = pyotp.TOTP(user['totp_secret'], interval=300)
        if totp.verify(totp_code):  # Verify TOTP code
            new_password = request.json.get('new_password')
            if new_password:
                user['password'] = new_password
                return render_template('reset_password.html', message="Password reset successfully")
            else:
                return render_template('reset_password.html', error="Invalid password")
        else:
            return render_template('reset_password.html', error="Invalid TOTP code")
    else:
        # If GET request, render the page
        return render_template('reset_password.html')

@app4.route('/reset/api/users/<username>/password', methods=['POST'])
def api_reset_password(username):
    user = app4_users.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    totp_code = request.json.get('totp_code')
    totp = pyotp.TOTP(user['totp_secret'], interval=300)
    if totp.verify(totp_code):  # Verify TOTP code
        new_password = request.json.get('new_password')
        if new_password:
            user['password'] = new_password
            return jsonify({"message": "Password reset successfully"})
        else:
            return jsonify({"error": "Invalid password"}), 400
    else:
        return jsonify({"error": "Invalid TOTP code"}), 400

@app4.route('/sales_document.html')
def sales_document():
    vin = request.args.get('vin', '')
    matching_users = [user for user, info in app4_users.items() if info['vin'] == vin]
    if matching_users:
        return render_template('sales_document.html', 
                               vin=vin, 
                               sales_document="Sensitive sales document content...", 
                               owner=app4_users[matching_users[0]]['email'])
    else:
        return render_template('sales_document.html', vin=vin, sales_document=None)

# API端点，返回JSON格式的TOTP码
@app4.route('/rest/api/chains/accounts/<username>/totp', methods=['POST'])
def api_get_totp(username):
    user = app4_users.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 使用 pyotp 生成 TOTP 码
    totp = pyotp.TOTP(user['totp_secret'], interval=300)
    totp_code = totp.now()
    return jsonify({"totp_code": totp_code})

if __name__ == '__main__':
    app1.run(host='0.0.0.0', port=5000)
    app2.run(host='0.0.0.0', port=5001)
    app3.run(host='0.0.0.0', port=5002)
    app4.run(host='0.0.0.0', port=5003)
