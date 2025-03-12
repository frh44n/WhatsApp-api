from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Replace with your actual credentials
ACCESS_TOKEN = "EAA4oGPOX6zsBO9OleVbTHZBA4DyHL6PMXINFElKoIzZBPuhZBTBVZCS13OPw6V2kAeoyrMRvG3KlDV3GPXxnonIrg5Q1gD0tAhZAtfMUZBV3275zqgEh2dTF1SX5vItdK97Sda030RTqFV7LMkvJwA9WC4XZB7gOeqrUDFXaFt7MPqdsvtlagHXTj7DZBfcBaVyzIgZDZD"
PHONE_NUMBER_ID = "602490136278649"

# In-memory storage for messages
messages = []

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

# Webhook Verification
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED SUCCESSFULLY!")
        return challenge, 200
    else:
        return "Verification failed", 403

# Receive messages from WhatsApp
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.json
    print("Webhook received data:", json.dumps(data, indent=2))  # Debugging log

    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # Ensure this is a message event
                if "messages" in value:
                    for msg in value["messages"]:
                        sender = msg.get("from", "Unknown")
                        msg_type = msg.get("type", "unknown")

                        if msg_type == "text":
                            message_text = msg["text"].get("body", "No text")
                        else:
                            message_text = f"Received {msg_type} message"

                        messages.append({"sender": sender, "message": message_text, "type": "received"})

    return jsonify({"status": "received"}), 200

# Send messages via WhatsApp API
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    recipient = data.get("recipient")
    text = data.get("text")

    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, headers=headers, json=payload)
    response_data = response.json()
    print("Send Message Response:", json.dumps(response_data, indent=2))  # Debugging log

    if response.status_code == 200:
        messages.append({"sender": "You", "message": text, "type": "sent"})
        return jsonify(response_data)
    else:
        return jsonify({"error": response_data}), 400

# Fetch all messages (For frontend display)
@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

if __name__ == '__main__':
    app.run(debug=True)
