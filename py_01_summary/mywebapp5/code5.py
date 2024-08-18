from flask import Flask, render_template, request, jsonify, redirect, url_for
import pyotp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 模拟的数据库
users_db = {
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

@app.route('/')
def home():
    return render_template('login.html')  # 修改首页为登录页面

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users_db.get(username)
        if user and user['password'] == password:
            # 登录成功，重定向到个人信息页面
            return redirect(url_for('user_info', username=username))
        else:
            # 登录失败，返回错误信息
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/user_info.html')
def user_info():
    username = request.args.get('username', '')
    user = users_db.get(username)
    if user:
        return render_template('user_info.html', user=user)
    else:
        return render_template('user_info.html', error="User not found")

@app.route('/totp_request.html')
def totp_request():
    username = request.args.get('username', '')
    user = users_db.get(username)
    if user:
        return render_template('totp_request.html', username=username)
    else:
        return render_template('totp_request.html', username=None)

@app.route('/totp.html')
def totp():
    username = request.args.get('username', '')
    user = users_db.get(username)
    if user:
        totp = pyotp.TOTP(user['totp_secret'], interval=300)  # Set interval to 300 seconds (5 minutes)
        totp_code = totp.now()  # Generate TOTP code
        return render_template('totp.html', totp_code=totp_code)
    else:
        return render_template('totp.html', totp_code=None)

@app.route('/reset_password.html', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.json.get('username')
        user = users_db.get(username)
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

@app.route('/reset/api/users/<username>/password', methods=['POST'])
def api_reset_password(username):
    user = users_db.get(username)
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

@app.route('/sales_document.html')
def sales_document():
    vin = request.args.get('vin', '')
    matching_users = [user for user, info in users_db.items() if info['vin'] == vin]
    if matching_users:
        return render_template('sales_document.html', 
                               vin=vin, 
                               sales_document="Sensitive sales document content...", 
                               owner=users_db[matching_users[0]]['email'])
    else:
        return render_template('sales_document.html', vin=vin, sales_document=None)

# API端点，返回JSON格式的TOTP码
@app.route('/rest/api/chains/accounts/<username>/totp', methods=['POST'])
def api_get_totp(username):
    user = users_db.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 使用 pyotp 生成 TOTP 码
    totp = pyotp.TOTP(user['totp_secret'], interval=300)
    totp_code = totp.now()
    return jsonify({"totp_code": totp_code})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

