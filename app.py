from flask import Flask, request, jsonify
import json
import os
import requests

app = Flask(__name__)

LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_SECRET = os.getenv("LINE_SECRET")

with open("drug_data.json", "r", encoding="utf-8") as f:
    drug_data = json.load(f)

def reply_image(reply_token, image_url, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url
            },
            {
                "type": "text",
                "text": text
            }
        ]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json
    for event in payload["events"]:
        if event["type"] == "message" and event["message"]["type"] == "text":
            query = event["message"]["text"].lower().strip()
            reply_token = event["replyToken"]

            if query in drug_data:
                info = drug_data[query]
                reply_image(reply_token, info["image"], f"ชื่อยา: {info['name']}")
            else:
                reply_image(reply_token, "https://via.placeholder.com/400x400.png?text=No+Image", "ไม่พบข้อมูลยา")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run()
