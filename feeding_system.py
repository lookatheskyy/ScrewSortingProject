# feeding_system.py

import time  
import RPi.GPIO as GPIO
import cv2
import numpy as np
import os
import conveyorbelt
import img_processing
import stepper_motor

# L298N控制IN1、IN2之类的GPIO口
FEEDER_MOTOR_PIN = 23  # 假设用GPIO23

GPIO.setmode(GPIO.BCM)
GPIO.setup(FEEDER_MOTOR_PIN, GPIO.OUT)

"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

进料系统
控制电机的启动和停止
具体的触发动作由主程序提供

驱动板：L298N

-------------------------------------------
feeding_system
trigger feeding_system
call by main program

——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""

def feedingsystem_start():
    """进料电机开启
    eng version: Start the feeding system motor
    """
    GPIO.output(FEEDER_MOTOR_PIN, GPIO.HIGH)
    print("Feeding system motor started.")

def feedingsystem_stop():
    """进料电机停止
    eng version: Stop the feeding system motor
    """
    GPIO.output(FEEDER_MOTOR_PIN, GPIO.LOW)
    print("Feeding system motor stopped.")

def cleanup():
    """清理GPIO设置
    eng version: Clean up GPIO settings
    """
    GPIO.output(FEEDER_MOTOR_PIN, GPIO.LOW)
    GPIO.cleanup()