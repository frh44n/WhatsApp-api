from flask import Flask, request, jsonify, render_template
import requests
import json
import os

app = Flask(__name__)

# Load credentials from config.json
CONFIG_FILE = "config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
        ACCESS_TOKEN = config.get("ACCESS_TOKEN", "")
        PHONE_NUMBER_ID = config.get("PHONE_NUMBER_ID", "")
        VERIFY_TOKEN = config.get("VERIFY_TOKEN", "")
else:
    raise FileNotFoundError(f"{CONFIG_FILE} not found. Please create it with your credentials.")

# Temporary storage for messages (both received & sent)
messages = []

# Webhook verification (for Meta)
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge
    return "Verification failed", 403

# Webhook to receive WhatsApp messages
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.json
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "messages" in change["value"]:
                    for msg in change["value"]["messages"]:
                        sender = msg["from"]
                        message_text = msg.get("text", {}).get("body", "Media Message")
                        messages.append({"sender": sender, "message": message_text})

    return jsonify({"status": "received"}), 200

# Route to fetch all messages for frontend
@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

# Route to send WhatsApp messages
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

    # Store sent message in memory
    messages.append({"sender": "Me", "message": text, "recipient": recipient})

    return jsonify(response.json())

# Home route to serve frontend
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
