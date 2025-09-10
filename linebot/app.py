import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from linebot.v3.webhooks import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, TextMessage, ReplyMessage, ImageMessage, RichMenuResponse
from dotenv import load_dotenv  # 導入 dotenv

# 載入 .env 檔案中的環境變數
load_dotenv()

# 從環境變數中讀取金鑰
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 檢查金鑰是否成功讀取，如果沒有則拋出錯誤
if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise ValueError("Missing LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_SECRET environment variables")

# 初始化 LINE Bot SDK
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
app = FastAPI()

# 接收 LINE 平台傳來的 Webhook 事件
@app.post("/callback")
async def handle_callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature or bad request")
    return "OK"

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        user_message = event.message.text
        reply_token = event.reply_token
        
        print(f"收到來自使用者 {event.source.user_id} 的訊息：{user_message}")
        
        # 在這裡放你的 chatbot 邏輯
        # 目前先簡單回覆使用者收到的訊息
        response_message = f"你說了：{user_message}"
        line_bot_api.reply_message_with_http_info(
            ReplyMessage(
                reply_token=reply_token,
                messages=[TextMessage(text=response_message)]
            )
        )

# 處理圖片訊息
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        reply_token = event.reply_token
        
        # 圖片訊息的處理方式會更複雜，需要取得內容
        print(f"收到來自使用者 {event.source.user_id} 的圖片訊息")
        response_message = "收到你的圖片了！稍後會處理分類功能。"
        line_bot_api.reply_message_with_http_info(
            ReplyMessage(
                reply_token=reply_token,
                messages=[TextMessage(text=response_message)]
            )
        )