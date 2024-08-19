from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import random

app = Flask(__name__)

# MQTT Broker settings
BROKER_ADDRESS = "broker.hivemq.com"  # Replace with your broker address
PORT = 1883
TOPIC = "sany/fleet/messages"

mqtt_client = mqtt.Client()

# MQTT connection callback
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(TOPIC)

# MQTT message callback
def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} {msg.payload.decode()}")

# Set callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(BROKER_ADDRESS, PORT, 60)
mqtt_client.loop_start()tt

# Route to publish a simple message
@app.route('/publish', methods=['POST'])
def publish():
    message = request.json.get('message')
    mqtt_client.publish(TOPIC, message)
    return jsonify({"status": "Message sent"})

# Route to create and publish a fake fleet message
@app.route('/create_fake_fleet_message', methods=['POST'])
def create_fake_fleet_message():
    fleet_id = request.json.get('fleet_id', f"fleet_{random.randint(1000, 9999)}")
    location = request.json.get('location', f"Location_{random.randint(1, 100)}")
    status = request.json.get('status', 'active')

    fake_message = {
        "fleet_id": fleet_id,
        "location": location,
        "status": status,
        "message": "This is a fake fleet message from Sany Heavy Industry"
    }

    mqtt_client.publish(TOPIC, jsonify(fake_message).get_data(as_text=True))
    return jsonify({"status": "Fake fleet message sent", "message": fake_message})

# Route to create a Sany Heavy Industry specific fleet message
@app.route('/create_sany_message', methods=['POST'])
def create_sany_message():
    equipment_id = request.json.get('equipment_id', f"SANY_{random.randint(1000, 9999)}")
    operation_status = request.json.get('operation_status', 'operational')
    fuel_level = request.json.get('fuel_level', f"{random.randint(10, 100)}%")

    sany_message = {
        "equipment_id": equipment_id,
        "operation_status": operation_status,
        "fuel_level": fuel_level,
        "message": "This is a Sany Heavy Industry fleet message"
    }

    mqtt_client.publish(TOPIC, jsonify(sany_message).get_data(as_text=True))
    return jsonify({"status": "Sany message sent", "message": sany_message})

# Run Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
