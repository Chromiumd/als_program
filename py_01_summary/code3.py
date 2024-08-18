from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt

app = Flask(__name__)

# MQTT Broker settings
BROKER_ADDRESS = "broker.hivemq.com"  #
PORT = 1883
TOPIC = "test/topic"


mqtt_client = mqtt.Client()

# MQTT连接回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(TOPIC)

# MQTT消息回调函数
def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} {msg.payload.decode()}")

# 设置回调
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(BROKER_ADDRESS, PORT, 60)
mqtt_client.loop_start()

@app.route('/publish', methods=['POST'])
def publish():
    message = request.json.get('message')
    mqtt_client.publish(TOPIC, message)
    return jsonify({"status": "Message sent"})


# 启动Flask服务器
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
