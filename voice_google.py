from gtts import gTTS
import os

# 1. 就定位後 說"準備開始拍照"
# 2. 說"準備開始拍照"後 倒數 "321"

def voice(text1):
    tts = gTTS(text = text1, lang='zh-TW')
    tts.save('hello_tw.mp3')
    os.system('omxplayer -o local -p hello_tw.mp3 > /dev/null 2>&1')
