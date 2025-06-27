import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Route ตรวจสอบสถานะ
@app.route('/')
def home():
    return 'LINE Drug Bot is running!'

# อ่าน LINE TOKEN และ SECRET จาก Environment Variable
LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_SECRET = os.getenv("LINE_SECRET")

# โหลดข้อมูลยา
with open("drug_data.json", "r", encoding="utf-8") as f:
    drug_data = json.load(f)

# ฟังก์ชันส่งข้อความ + รูป
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

# ฟังก์ชันส่งเฉพาะข้อความ
def reply_text(reply_token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

# Webhook จาก LINE
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json
    for event in payload["events"]:
        if event["type"] == "message" and event["message"]["type"] == "text":
            query = event["message"]["text"].lower().strip()
            reply_token = event["replyToken"]

            if query in drug_data:
                info = drug_data[query]
                reply_image(reply_token, info["image"], info["text"])
            else:
                reply_text(reply_token, "ไม่พบข้อมูล")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
