from flask import Flask, render_template, session, redirect, url_for, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app)

# 模拟的用户数据
users = {
    'user1@toyota.com': {'password': 'password1', 'info': 'User 1 Information'},
    'user2@toyota.com': {'password': 'password2', 'info': 'User 2 Information'},
    'user3@toyota.com': {'password': 'password3', 'info': 'User 3 Information'},
    'user4@toyota.com': {'password': 'password4', 'info': 'User 4 Information'},
    'user5@toyota.com': {'password': 'password5', 'info': 'User 5 Information'}
}

@app.route('/')
def index():
    return render_template('main_login.html')

@app.route('/toyota_login')
def toyota_login():
    return render_template('toyota_login.html')

@app.route('/login', methods=['POST'])
def login_api():
    # 尝试验证 JWT
    try:
        verify_jwt_in_request()
        # 如果 JWT 有效，直接跳过密码验证并登录
        email = get_jwt_identity()
        session['token'] = request.headers.get('Authorization').split()[1]  # 使用现有的 JWT
        return redirect(url_for('dashboard'))
    except Exception as e:
        # 如果 JWT 验证失败，继续处理登录表单
        pass
    
    # 正常的用户名和密码验证
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        return '缺少邮箱或密码', 400
    
    user = users.get(email)
    if user and user['password'] == password:
        access_token = create_access_token(identity=email)
        session['token'] = access_token
        return redirect(url_for('dashboard'))
    return '登录失败', 401

@app.route('/dashboard')
@jwt_required()
def dashboard():
    # 获取所有用户列表以传递到模板
    toyota_users = list(users.keys())
    return render_template('dashboard.html', toyota_users=toyota_users)

@app.route('/survey/<email>')
@jwt_required()
def survey(email):
    # 根据用户的邮箱获取个人信息
    user_info = users.get(email, {}).get('info', 'No information available')
    return render_template('survey.html', user_info=user_info)

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('index'))

@app.route('/generate_jwt', methods=['POST'])
def generate_jwt():
    email = request.form.get('email')
    if email in users:
        token = create_access_token(identity=email)
        return token
    return '用户不存在', 404

@app.before_request
def require_login():
    endpoint = request.endpoint
    if endpoint not in ('index', 'login_api', 'toyota_login', 'generate_jwt') and 'token' not in session:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

