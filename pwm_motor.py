#!/usr/bin/python 
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|R|a|s|p|b|e|r|r|y|P|i|.|c|o|m|.|t|w|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Copyright (c) 2016, raspberrypi.com.tw
# All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# pwm_motor.py
# Control car with PWM
#
# Author : sosorry
# Date   : 08/01/2015

import RPi.GPIO as GPIO
import time
import readchar

Motor_R1_Pin = 16
Motor_R2_Pin = 18
Motor_L1_Pin = 7
Motor_L2_Pin = 36
t = 0.1
dc = 50


GPIO.setmode(GPIO.BOARD)
GPIO.setup(Motor_R1_Pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor_R2_Pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor_L1_Pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor_L2_Pin, GPIO.OUT, initial=GPIO.LOW)

pwm_r1 = GPIO.PWM(Motor_R1_Pin, 500)
pwm_r2 = GPIO.PWM(Motor_R2_Pin, 500)
pwm_l1 = GPIO.PWM(Motor_L1_Pin, 500)
pwm_l2 = GPIO.PWM(Motor_L2_Pin, 500)
pwm_r1.start(0)
pwm_r2.start(0)
pwm_l1.start(0)
pwm_l2.start(0)


def stop():
    pwm_r1.ChangeDutyCycle(0)
    pwm_r2.ChangeDutyCycle(0)
    pwm_l1.ChangeDutyCycle(0)
    pwm_l2.ChangeDutyCycle(0)

def forward1():
    for i in range(27):
    
        if i%5 == 0 and i!=0:
            pwm_r1.ChangeDutyCycle(0)
            pwm_r2.ChangeDutyCycle(0)
            pwm_l1.ChangeDutyCycle(60)
            pwm_l2.ChangeDutyCycle(0)
            print(i)
            
            time.sleep(0.07)
        else:
            pwm_r1.ChangeDutyCycle(50)
            pwm_r2.ChangeDutyCycle(0)
            pwm_l1.ChangeDutyCycle(80)
            pwm_l2.ChangeDutyCycle(0)
            time.sleep(0.4)
        stop()

    
def backward1():
    
    for i in range(70):  
        if i%10 == 0 and i>0:
            pwm_r1.ChangeDutyCycle(0)
            pwm_r2.ChangeDutyCycle(0)
            pwm_l1.ChangeDutyCycle(0)
            pwm_l2.ChangeDutyCycle(60)  ##change here
            print(i)
                
            time.sleep(0.04)
        else:
            pwm_r1.ChangeDutyCycle(0)
            pwm_r2.ChangeDutyCycle(72)
            pwm_l1.ChangeDutyCycle(0)
            pwm_l2.ChangeDutyCycle(80)
            time.sleep(0.2)
                
        stop()        


def turnLeft(dis):  
    pwm_r1.ChangeDutyCycle(60)
    pwm_r2.ChangeDutyCycle(0)
    pwm_l1.ChangeDutyCycle(0)
    pwm_l2.ChangeDutyCycle(0)
    time.sleep(dis*0.01)
    stop()
    time.sleep(0.5)

def turnRight(dis):
    pwm_r1.ChangeDutyCycle(0)
    pwm_r2.ChangeDutyCycle(60)
    pwm_l1.ChangeDutyCycle(0)
    pwm_l2.ChangeDutyCycle(0)
    time.sleep(dis*0.01)
    stop()
    time.sleep(0.5)

def cleanup():
    stop()
    pwm_r1.stop()
    pwm_r2.stop()
    pwm_l1.stop()
    pwm_l2.stop()
    GPIO.cleanup()


if __name__ == "__main__":

    print("Press 'q' to quit...")

    while True:
        ch = readchar.readkey()

        if ch == 'w':
            forward1()

        elif ch == 's':
            backward1()

        elif ch == 'd':
            turnRight2()
            
        elif ch == 'f':
            turnRight1()

        elif ch == 'a':
            turnLeft1()
            
        elif ch == 'x':
            left()
            
        elif ch == 'c':
            right()
            
        elif ch == 'z':
            turnLeft2()

        elif ch == 'q':
            print("\nQuit")
            GPIO.cleanup()
            quit()

