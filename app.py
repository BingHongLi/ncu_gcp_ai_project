import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from flask import Flask, request, abort

from flask_cors import CORS


from linebot.exceptions import (
    InvalidSignatureError
)


from controllers.line_bot_controller import LineBotController

from controllers.user_controller import UserController

app = Flask(__name__)
CORS(app)

from linebot import (
    LineBotApi, WebhookHandler
)
import os
line_bot_api=LineBotApi(channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler=WebhookHandler(channel_secret=os.environ["LINE_CHANNEL_SECRET"])


# 載入Follow事件
from linebot.models.events import (
    FollowEvent,UnfollowEvent,MessageEvent,TextMessage,PostbackEvent,ImageMessage,AudioMessage,VideoMessage
)


# 建立日誌紀錄設定檔
# https://googleapis.dev/python/logging/latest/stdlib-usage.html
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler


client = google.cloud.logging.Client()

# 建立line event log，用來記錄line event
bot_event_handler = CloudLoggingHandler(client,name="ncu_bot_event")
bot_event_logger=logging.getLogger('ncu_bot_event')
bot_event_logger.setLevel(logging.INFO)
bot_event_logger.addHandler(bot_event_handler)

app = Flask(__name__)

@app.route('/test')
def hello_world():
    bot_event_logger.info("test")
    return 'Hello, World!'

'''
轉發功能列表
'''
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    bot_event_logger.info(body)
    # print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(FollowEvent)
def handle_line_follow(event):
    return LineBotController.follow_event(event)

@handler.add(UnfollowEvent)
def handle_line_unfollow(event):
    return LineBotController.unfollow_event(event)

@handler.add(MessageEvent,TextMessage)
def handle_line_text(event):
    return LineBotController.handle_text_message(event)

@handler.add(MessageEvent,ImageMessage)
def handle_line_image(event):
    return LineBotController.handle_image_message(event)

@handler.add(MessageEvent,VideoMessage)
def handle_line_video(event):
    return LineBotController.handle_video_message(event)

@handler.add(MessageEvent,AudioMessage)
def handle_line_audio(event):
    return LineBotController.handle_audio_message(event)

@handler.add(PostbackEvent)
def handle_postback_event(event):
    return LineBotController.handle_postback_event(event)

@app.route("/user",methods=['GET'])
def get_user():
    result = UserController.get_user(request)
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))