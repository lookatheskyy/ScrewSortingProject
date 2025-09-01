import time
#import RPi.GPIO as GPIO  
import cv2
import numpy as np
import os

import sensors
import conveyorbelt
import img_processing
import classification
import stepper_motor


"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

主函数：
1.基本设置
灯光常亮

2.控制流程
通电后自动启动：进料系统的电机、传送带电机、环形灯、传感器→ 传感器检测到物体→ 传送带停止建→ 获取照片并进行图像处理→ 进行分类→ 步进电机启动→ 传送带重启→ 步进电机复位（通过延时复位）

-------------------------------------------

Main Function:
1. Basic Settings
Lights Always On
Camera Resolution Settings

2. Control Flow
Automatically starts after power is turned on: feeding system motor, conveyor belt motor, ring light, sensor → 
sensor detects object → conveyor belt stops → photo is acquired and image processed → classification is performed → 
stepper motor starts → conveyor belt restarts → stepper motor resets (via timer reset)
——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""

class RingLight:
    def __init__(self, pin=18):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
    
    def turn_on(self):
        GPIO.output(self.pin, GPIO.HIGH)
    
    def turn_off(self):
        GPIO.output(self.pin, GPIO.LOW)
    
    def cleanup(self):
        GPIO.output(self.pin, GPIO.LOW)
        GPIO.cleanup()




def main():
    
    roi = (2, 395, 1911, 280)
    pixel_to_mm = 0.05


    try:
         # 1. 拍摄图片并保存
        image_path = camera.capture_image()
        print(f"Image captured and saved to {image_path}")

        # 2. 读取图片并检测
        
        
        result = img_processing.img_recog(image_path, roi, pixel_to_mm)
        
        print('Detection result:')
        print(f"Part type: {result['part_type']}")
        print(f"Length: {result['length_px']:.1f} px / {result['length_mm']:.2f} mm")
        print(f"Diameter: {result['diameter_px']:.1f} px / {result['diameter_mm']:.2f} mm")
        print(f"Angle: {result['angle']:.1f} degrees")
        print(f"Aspect ratio: {result['aspect_ratio']:.2f}")

        # 3. 进行型号分类
        model = classification.classify_model(result)
        print(f'Matched Model: {model}')

    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    main()
