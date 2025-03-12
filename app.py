from flask import Flask, request, jsonify
import sqlite3
import requests

app = Flask(__name__)

# WhatsApp API Credentials
WHATSAPP_API_URL = "https://graph.facebook.com/v21.0/602490136278649/messages"
ACCESS_TOKEN = "EAA4oGPOX6zsBO9OleVbTHZBA4DyHL6PMXINFElKoIzZBPuhZBTBVZCS13OPw6V2kAeoyrMRvG3KlDV3GPXxnonIrg5Q1gD0tAhZAtfMUZBV3275zqgEh2dTF1SX5vItdK97Sda030RTqFV7LMkvJwA9WC4XZB7gOeqrUDFXaFt7MPqdsvtlagHXTj7DZBfcBaVyzIgZDZD"

# Initialize Database
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            message TEXT,
            media_url TEXT,
            direction TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Webhook to Receive Messages
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "messages" in data["entry"][0]["changes"][0]["value"]:
        for msg in data["entry"][0]["changes"][0]["value"]["messages"]:
            phone = msg["from"]
            message = msg.get("text", {}).get("body", "")
            media_url = msg.get("image", {}).get("id", None)

            conn = sqlite3.connect("chat.db")
            c = conn.cursor()
            c.execute("INSERT INTO messages (phone, message, media_url, direction) VALUES (?, ?, ?, ?)",
                      (phone, message, media_url, "received"))
            conn.commit()
            conn.close()
    return "OK", 200

# Get Chat List (Unique Users)
@app.route("/chats", methods=["GET"])
def get_chats():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT DISTINCT phone FROM messages")
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(users)

# Get Messages for a User
@app.route("/messages/<phone>", methods=["GET"])
def get_messages(phone):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT message, media_url, direction FROM messages WHERE phone = ?", (phone,))
    messages = [{"text": row[0], "media": row[1], "direction": row[2]} for row in c.fetchall()]
    conn.close()
    return jsonify(messages)

# Send Message
@app.route("/send", methods=["POST"])
def send_message():
    data = request.json
    phone = data["phone"]
    message = data["message"]

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message}
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        conn = sqlite3.connect("chat.db")
        c = conn.cursor()
        c.execute("INSERT INTO messages (phone, message, direction) VALUES (?, ?, ?)",
                  (phone, message, "sent"))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": response.json()}), 400

if __name__ == "__main__":
    app.run(debug=True)
