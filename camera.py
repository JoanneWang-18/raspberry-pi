# import the necessary packages
from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import pwm_motor as p
import time
import threading
import voice_google
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import ultrasound
import mcp
import RPi.GPIO as GPIO
import json
from imgurpython import ImgurClient
from datetime import datetime
import pyimgur

#import request
# construct the argument parse and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-i", "--images", required=True, help="path to images directory")
#args = vars(ap.parse_args())

# initialize the HOG descriptor/person detector

# loop over the image paths

GPIO.setmode(GPIO.BOARD)
 
GPIO_LED = 22
GPIO.setup(GPIO_LED, GPIO.OUT)

global t0_start
global new_center
global background_check
global t_speaker
global old_time

def compare(x,y,w,h):
    global t0_start
    global new_center
    #new_center = (x+w/2)
    t0_start = True
    print(new_center)
    if new_center < 65:
        p.turnLeft(abs(new_center - 75))
    elif new_center > 85:
        p.turnRight(abs(new_center - 75))
    t0_start = False
        
    
# 當地端程式連線伺服器得到回應時，要做的動作
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # 將訂閱主題寫在on_connet中
    # 如果我們失去連線或重新連線時 
    # 地端程式將會重新訂閱
    client.subscribe("Try/MQTT~~")

# 當接收到從伺服器發送的訊息時要進行的動作
def on_message(client, userdata, msg):
    # 轉換編碼utf-8才看得懂中文
    global background_check
    print(msg.topic+" "+ msg.payload.decode('utf-8'))
    background_check = True


def receive():
    # 連線設定
    # 初始化地端程式
    client = mqtt.Client()

    # 設定連線的動作
    client.on_connect = on_connect

    # 設定接收訊息的動作
    client.on_message = on_message

    # 設定登入帳號密碼
    client.username_pw_set("mumu2","789")

    # 設定連線資訊(IP, Port, 連線時間)
    client.connect("140.138.152.94", 1883, 60)
    # 開始連線，執行設定的動作和處理重新連線問題
    # 也可以手動使用其他loop函式來進行連接
    client.loop_forever()


def speaker():
    global t_speaker
    t_speaker = True
    voice_google.voice("請使用者方向對準鏡頭 並前後移動調整至適當距離")
    t_speaker = False


def humanDetector():
    global t0_start
    global background_check
    global new_center
    global t_speaker
    global old_time
    

    video = cv2.VideoCapture(0)
    
    voice_google.voice("請使用者開始左右移動至想要的拍攝位置")
    time.sleep(0.5)

    t = threading.Thread(target = receive)
    t.start()
    
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    while background_check == False:
        # load the image and resize it to (1) reduce detection time
        # and (2) improve detection accuracy
        if mcp.light() < 300:
            GPIO.output(GPIO_LED, True)
        else:
            GPIO.output(GPIO_LED, False)
        
        check, image = video.read()
        if check:
            
            
            image = imutils.resize(image, width=min(150, image.shape[1]))
            #orig = image.copy()

            # detect people in the image
            (rects, weights) = hog.detectMultiScale(image, winStride=(2, 2),
                padding=(32, 32), scale=1.05)
            
            #for i, (x, y, w, h) in enumerate(rects):
                #print(weights[i])
            
            if len(rects) != 0:
                old_time = time.time()
                
                for i, (x, y, w, h) in enumerate(rects):
                    print(x,y,w,h)
                    new_center = (x+w/2)
                    if weights[i] < 0.3:
                        continue
                    #if weights[i] < 0.3 and weights[i] > 0.25:
                    #    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    if weights[i] < 0.6 and weights[i] > 0.3:
                        if t0_start == False:
                            t0 = threading.Thread(target = compare,args=(x,y,w,h))
                            t0.start()
                        cv2.rectangle(image, (x, y), (x+w, y+h), (50, 122, 255), 2)
                    if weights[i] > 0.6:
                        if t0_start == False:
                            t0 = threading.Thread(target = compare,args=(x,y,w,h))
                            t0.start()
                        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            else:
                if t_speaker == False and time.time() - old_time > 3:
                    sp = threading.Thread(target = speaker)
                    sp.start()
            # draw the original bounding boxes
            #for (x, y, w, h) in rects:
            #    cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # apply non-maxima suppression to the bounding boxes using a
            # fairly large overlap threshold to try to maintain overlapping
            # boxes that are still people
            rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
            pick = non_max_suppression(rects, probs=None, overlapThresh=0.3)

            # draw the final bounding boxes
            #for (xA, yA, xB, yB) in pick:
                #cv2.rectangle(image, (xA, yA-50), (xB, yB+50), (0, 255, 0), 2)

            # show some information on the number of bounding boxes
            #filename = imagePath[imagePath.rfind("/") + 1:]
            #print("[INFO] {}: {} original boxes, {} after suppression".format(
                    #filename, len(rects), len(pick)))

            # show the output images
            #cv2.imshow("Before NMS", orig)
            cv2.imshow("After NMS", image)
            key = cv2.waitKey(1)
            if key== ord('q'):
                break
            #time.sleep(1)
            
        else:
            print("no image")
            
    else:
        #start counting down
        time.sleep(2)
        
        while t_speaker == True:
            pass
                            
        voice_google.voice("開始偵測兩公尺內是否有人")
        
        time.sleep(4)
        while ultrasound.distance() < 200:
            voice_google.voice("嘿 前面的人 你擋到我拍照了")
            time.sleep(2)
        else:
            voice_google.voice("確認前方已無人")
        
        #time.sleep(0.5)
        voice_google.voice("請擺出拍照姿勢")
        time.sleep(0.5)
        voice_google.voice("三")
        time.sleep(0.5)
        voice_google.voice("二")
        time.sleep(0.5)
        voice_google.voice("一")
        time.sleep(0.5)
        voice_google.voice("咖擦")
        
        
        check, image = video.read()
        if check:
            cv2.imwrite('output.jpg', image)
     
            # 連線設定
            # 初始化地端程式
            client = mqtt.Client()

            # 設定登入帳號密碼
            client.username_pw_set("mumu1","456")

            # 設定連線資訊(IP, Port, 連線時間)
            client.connect("140.138.152.94", 1883, 60)
            
            
            CLIENT_ID = "dda7aeb453dba34"
            PATH = "output.jpg"
            

            im = pyimgur.Imgur(CLIENT_ID)
            uploaded_image = im.upload_image(PATH, title="Uploaded with PyImgur")
            print(uploaded_image.link)

            image_url = uploaded_image.link

            payload = {'image_url' : image_url}
    
            client.publish("Try/MQTT!!", json.dumps(payload))
     
            
            
        else:
            print("no image")

     
     
    video.release()
    cv2.destroyAllWindows()
def main():
    global t0_start
    global background_check
    global t_speaker
    global old_time
    old_time = time.time()
    background_check = False
    t0_start = False
    t_speaker = False
    
    humanDetector()
    


if __name__ == "__main__":
    main()