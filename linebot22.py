from flask import Flask
app = Flask(__name__)

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import paho.mqtt.client as mqtt
import requests
import time
import sqlite3
import threading

import random
import json  
import datetime 


#line_bot
line_bot_api = LineBotApi('UfmyplApRUQeBA7f9WMfTfCnwnL3aWrS5Ujeunnz3crNj4cJoG3XtnTQLThdRBlClS1bFaY1zTsTLfrP/Eltuf6hcU1Q3AqnTawUyIOhkU2Q/XiN+tiIBi786QdZdplcPgAPcgyQy/CImEw2/YZNMAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('c911ab697c1a9784809a7e968a4f5b87')

global line_id
global one_user

# 當地端程式連線伺服器得到回應時，要做的動作
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # 將訂閱主題寫在on_connet中
    # 如果我們失去連線或重新連線時 
    # 地端程式將會重新訂閱
    client.subscribe("Try/MQTT!!")

# 當接收到從伺服器發送的訊息時要進行的動作
def on_message(client, userdata, msg):
    global one_user
    # 轉換編碼utf-8才看得懂中文
    if one_user == True:
        print(msg.topic+" "+ msg.payload.decode('utf-8'))
        send_photo(msg.payload.decode('utf-8'))


# 子執行緒的工作函數
def job():
    global line_id
    global one_user
    one_user = False
    line_id = None
    # 連線設定
    # 初始化地端程式
    client2 = mqtt.Client()

    # 設定連線的動作
    client2.on_connect = on_connect

    # 設定接收訊息的動作
    client2.on_message = on_message

    # 設定登入帳號密碼
    client2.username_pw_set("mumu1","456")

    # 設定連線資訊(IP, Port, 連線時間)
    client2.connect("140.138.152.94", 1883, 60)
    # 開始連線，執行設定的動作和處理重新連線問題
    # 也可以手動使用其他loop函式來進行連接
    client2.loop_forever()


def user():
    
    # 連線設定
    # 初始化地端程式
    client = mqtt.Client()

    # 設定登入帳號密碼
    client.username_pw_set("mumu","123")

    # 設定連線資訊(IP, Port, 連線時間)
    client.connect("140.138.152.94", 1883, 60)

    payload = {'ok' : 1}

    client.publish("Try/MQTT", json.dumps(payload))


@app.route("/callback",methods = ['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global one_user
    global line_id
    mtext = event.message.text
    if mtext == '我要拍照':  #用ubidots
        try:
            #print(one_user)
            if one_user == False:
                one_user = True
                line_id = line_bot_api.get_profile(event.source.user_id).user_id
                pi_start = threading.Thread(target = user)
                pi_start.start()
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="連線至樹莓派"))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="目前有人正在使用PiBot"))

            print(one_user)
            
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='拍照失敗1'))
    
    elif mtext == '可以拍照了':
        try:
            temp_id = line_bot_api.get_profile(event.source.user_id).user_id
            if one_user == True and temp_id == line_id:
                # 連線設定
                # 初始化地端程式
                client = mqtt.Client()

                # 設定登入帳號密碼
                client.username_pw_set("mumu2","789")

                # 設定連線資訊(IP, Port, 連線時間)
                client.connect("140.138.152.94", 1883, 60)

                payload = {'ok':1}

                client.publish("Try/MQTT~~", json.dumps(payload))

            elif temp_id != line_id:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="目前有人正在使用PiBot"))
            elif one_user == False:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="目前沒有使用者連至PiBot，請先點擊'我要拍照'"))
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='拍照失敗2'))


def send_photo(photo):
    global line_id
    global one_user


    image_url = photo[photo.find("https"):photo.find(".jpg")+4]
    #print(image_url)
    line_bot_api.push_message(line_id,ImageSendMessage(original_content_url = image_url, preview_image_url = image_url))
    one_user = False


if __name__ == "__main__":
    print(1)
    
    # 建立一個子執行緒
    t = threading.Thread(target = job)

    # 執行該子執行緒
    t.start()
    print(1)

    app.run(debug=True)
    