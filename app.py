from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "8672602713:AAGU-ItnzN5u_fwOn5k1njCQyrX219gotYI"
CHAT_ID = "8772042549"

@app.route('/webhook', methods=['POST'])
def webhook():

    data = request.json

    message = data.get("message", "Signal")

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        }
    )

    return "OK"

if __name__ == "__main__":
    app.run()
