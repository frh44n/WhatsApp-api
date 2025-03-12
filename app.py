from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Temporary storage for received messages
messages = []

# Your WhatsApp API credentials
ACCESS_TOKEN = "EAA4oGPOX6zsBO9OleVbTHZBA4DyHL6PMXINFElKoIzZBPuhZBTBVZCS13OPw6V2kAeoyrMRvG3KlDV3GPXxnonIrg5Q1gD0tAhZAtfMUZBV3275zqgEh2dTF1SX5vItdK97Sda030RTqFV7LMkvJwA9WC4XZB7gOeqrUDFXaFt7MPqdsvtlagHXTj7DZBfcBaVyzIgZDZD"
PHONE_NUMBER_ID = "602490136278649"

# Webhook verification route
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    VERIFY_TOKEN = "zapexy"  # Set this in Meta Developer Portal
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge
    else:
        return "Verification failed", 403

# Route to receive WhatsApp messages
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

# Route to fetch messages for frontend
@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

# Route to send a message
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
    return jsonify(response.json())

# Home route to serve frontend
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
