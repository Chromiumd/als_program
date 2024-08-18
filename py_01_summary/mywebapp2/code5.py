from flask import Flask, request, jsonify
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 模拟的数据库
users_db = {
    "john.doe": {
        "email": "john.doe@example.com",
        "password": "securepassword123",
        "totp_secret": "JBSWY3DPEHPK3PXP",  # 模拟的TOTP密钥
        "vin": "1HGCM82633A123456"
    },
    "jane.smith": {
        "email": "jane.smith@example.com",
        "password": "anotherpassword456",
        "totp_secret": "KVKFKRCPNZQUYMLX",
        "vin": "1HGCM82633A654321"
    }
}

# 模糊用户查询接口
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

    # 验证TOTP码
    totp_code = request.json.get('totp_code')
    if totp_code and totp_code == "123456":  # 演示中的TOTP码是固定的，模拟存在漏洞
        new_password = request.json.get('new_password')
        if new_password:
            user['password'] = new_password
            return jsonify({"message": "Password reset successfully"})
        else:
            return jsonify({"error": "Invalid password"}), 400
    else:
        return jsonify({"error": "Invalid TOTP code"}), 401

# 获取车辆销售文档（包含敏感信息）
@app.route('/rest/api/vehicles/<vin>/sales_document', methods=['GET'])
def get_sales_document(vin):
    matching_users = [user for user, info in users_db.items() if info['vin'] == vin]
    if matching_users:
        # 模拟返回包含敏感信息的销售文档
        return jsonify({
            "vin": vin,
            "sales_document": "Sensitive sales document content...",
            "owner": users_db[matching_users[0]]['email']
        })
    else:
        return jsonify({"error": "No matching VIN found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

