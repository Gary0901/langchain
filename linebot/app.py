import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
# 將 WebhookParser 替換為 WebhookHandler
from linebot.v3.webhooks import WebhookHandler, MessageEvent, TextMessageContent, ImageMessageContent
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, TextMessage, ReplyMessage
from dotenv import load_dotenv

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
# 將 WebhookParser 替換為 WebhookHandler
handler = WebhookHandler(LINE_CHANNEL_SECRET)
app = FastAPI()

# 接收 LINE 平台傳來的 Webhook 事件
@app.post("/callback")
async def handle_callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()
    try:
        # 使用 WebhookHandler 來解析 Webhook 事件，它會回傳一個事件列表
        events = handler.handle(body.decode("utf-8"), signature)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature or bad request")

    # 迴圈處理每一個事件
    for event in events:
        # 只處理訊息事件
        if isinstance(event, MessageEvent):
            handle_message_event(event)
            
    return "OK"

# 將處理邏輯獨立出來的函式
def handle_message_event(event: MessageEvent):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        reply_token = event.reply_token

        # 處理文字訊息
        if isinstance(event.message, TextMessageContent):
            user_message = event.message.text
            print(f"收到來自使用者 {event.source.user_id} 的文字訊息：{user_message}")
            response_message = f"你說了：{user_message}"
            line_bot_api.reply_message_with_http_info(
                ReplyMessage(
                    reply_token=reply_token,
                    messages=[TextMessage(text=response_message)]
                )
            )

        # 處理圖片訊息
        elif isinstance(event.message, ImageMessageContent):
            print(f"收到來自使用者 {event.source.user_id} 的圖片訊息")
            response_message = "收到你的圖片了！稍後會處理分類功能。"
            line_bot_api.reply_message_with_http_info(
                ReplyMessage(
                    reply_token=reply_token,
                    messages=[TextMessage(text=response_message)]
                )
            )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
