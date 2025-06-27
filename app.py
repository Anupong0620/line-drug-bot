from flask import Flask, request, jsonify
import json
import os
import requests

app = Flask(__name__)

# Route สำหรับตรวจสอบสถานะ
@app.route('/')
def home():
    return 'LINE Drug Bot is running!'

# อ่าน LINE TOKEN และ SECRET จาก Environment Variable
LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_SECRET = os.getenv("LINE_SECRET")

# โหลดข้อมูลยา
with open("drug_data.json", "r", encoding="utf-8") as f:
    drug_data = json.load(f)

# ฟังก์ชันส่งภาพและข้อความกลับ
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

    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=headers,
        json=body
    )

# Webhook route สำหรับรับข้อความจาก LINE
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json

    for event in payload.get("events", []):
        if event.get("type") == "message" and event["message"].get("type") == "text":
            query = event["message"]["text"].lower().strip()
            reply_token = event["replyToken"]

            if query in drug_data:
                info = drug_data[query]
                image_url = info.get("image", "https://via.placeholder.com/400x400.png?text=No+Image")
                text = info.get("text", "ไม่พบรายละเอียด")
            else:
                image_url = "https://via.placeholder.com/400x400.png?text=No+Image"
                text = "ไม่พบข้อมูลยา"

            reply_image(reply_token, image_url, text)

    return jsonify({"status": "ok"})

# รันแอป
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
