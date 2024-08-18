from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

# 模拟的数据库
users_db = {
    "john.doe": {
        "email": "john.doe@example.com",
        "password": "securepassword123",
        "totp_secret": "JBSWY3DPEHPK3PXP"  #
    },
    "jane.smith": {
        "email": "jane.smith@example.com",
        "password": "anotherpassword456",
        "totp_secret": "KVKFKRCPNZQUYMLX"
    }
}


# 模拟的模糊用户查询接口
@app.route('/rest/api/users/<username>', methods=['GET'])
def get_user_info(username):
    matching_users = {user: info for user, info in users_db.items() if username in user}
    if matching_users:
        return jsonify(matching_users)
    else:
        return jsonify({"error": "No users found"}), 404


# 基于时间的一次性密码接口（TOTP）
@app.route('/rest/api/chains/accounts/<username>/totp', methods=['POST'])
def get_totp(username):
    user = users_db.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 生成一个TOTP码
    totp_code = str(random.randint(100000, 999999))
    return jsonify({"totp_code": totp_code})


# 密码重置接口
@app.route('/reset/api/users/<username>/password', methods=['POST'])
def reset_password(username):
    user = users_db.get(username)
    if not user:
        return jsonify({"error": "User not found"}), 404

    #户密码重置
    new_password = request.json.get('new_password')
    if new_password:
        user['password'] = new_password
        return jsonify({"message": "Password reset successfully"})
    else:
        return jsonify({"error": "Invalid password"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)