from flask import Flask, render_template, session, redirect, url_for, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app)

# Simulated user data
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
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Check if the username and password are correct
    user = users.get(email)
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

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in via session
    if 'email' in session:
        toyota_users = list(users.keys())
        return render_template('dashboard.html', toyota_users=toyota_users)
    
    # If not logged in, show a simplified dashboard with options only
    toyota_users = []  # No user-specific information
    return render_template('dashboard_simplified.html', toyota_users=toyota_users)

@app.route('/survey/<email>')
def survey(email):
    if 'email' not in session:
        return redirect(url_for('index'))
    
    user_info = users.get(email, {}).get('info', 'No information available')
    return render_template('survey.html', user_info=user_info)

@app.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('email', None)
    response = redirect(url_for('index'))
    unset_jwt_cookies(response)
    return response

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
    if endpoint in ['survey', 'dashboard'] and 'email' not in session:
        # Allow access to a simplified dashboard but enforce login for other routes
        if endpoint == 'dashboard':
            return None
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

