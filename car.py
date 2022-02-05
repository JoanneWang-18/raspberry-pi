# !/usr/bin/python
# coding:utf-8



import pwm_motor as p
import camera
import voice_google
import paho.mqtt.client as mqtt
import time
import threading


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    client.subscribe("Try/MQTT")

def on_message(client, userdata, msg):
    print(msg.topic+" "+ msg.payload.decode('utf-8'))
    start_work(msg.payload.decode('utf-8'))
    


def job():
    client = mqtt.Client()

    client.on_connect = on_connect

    client.on_message = on_message

    client.username_pw_set("mumu","123")

    client.connect("140.138.152.94", 1883, 60)
  
    client.loop_forever()


def start_work(line_id):
    #get ready to backward
    time.sleep(2)
    voice_google.voice("開始倒退抓取拍攝距離")
    p.backward1()
    
    
    #adapting the position
    time.sleep(2)  #please face to camera!!!!!!!!!
    camera.main()#send "ok" to car
    
    voice_google.voice("拍照完成")
    p.forward1()


if __name__ == "__main__":
    global count
    count = 0
    t = threading.Thread(target = job)

    t.start()
    
    
    
    

    
    
    