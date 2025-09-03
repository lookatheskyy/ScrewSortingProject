import time
import RPi.GPIO as GPIO  
import cv2
import numpy as np
import os
import sensors
import conveyorbelt
import img_processing
import classification
from stepper_motor import StepperMotorController 
import camera





"""
————————————————————————————————————————————————————————————————————————————————————————————————————————


控制流程
step 1 ：通电后自动启动：进料系统的电机、传送带电机、环形灯、传感器→ 
step 2 ：送入目标检测物 →
step 3 ：传感器检测到物体→ 
step 4 ：传送带停止→ 
step 5 ：获取照片并进行图像处理→ 
step 6 ：进行分类→ 
step 7 ：步进电机启动→ 
step 8 ：传送带重启→ 
step 9 ：步进电机复位（通过延时复位）→
step 10 ：回到第二步


-------------------------------------------
English：
Control Flow
Step 1: Automatically activate the feed system motor, conveyor motor, ring light, and sensor upon power-up.
Step 2: Feed the target object.
Step 3: Sensor detects the object.
Step 4: Conveyor stops.
Step 5: Capture a photo and perform image processing.
Step 6: Classify the items.
Step 7: Start the stepper motor.
Step 8: Restart the conveyor.
Step 9: Reset the stepper motor (via a timer reset).
Step 10: Return to step 2.

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
         # 1. Take a picture and save it 拍摄图片并保存 
        image_path = camera.capture_image()
        print(f"Image captured and saved to {image_path}")

        # 2. Read the image and detect 读取图片并检测
        result = img_processing.img_recog(image_path, roi, pixel_to_mm)
        print('Detection result:')
        print(f"Part type: {result['part_type']}")
        print(f"Length: {result['length_px']:.1f} px / {result['length_mm']:.2f} mm")
        print(f"Diameter: {result['diameter_px']:.1f} px / {result['diameter_mm']:.2f} mm")
        print(f"Angle: {result['angle']:.1f} degrees")
        print(f"Aspect ratio: {result['aspect_ratio']:.2f}")

        # 3. Classify 进行型号分类
        model = classification.classify_model(result)
        print(f'Matched Model: {model}')

        # 4. Control the stepper motor to rotate to the corresponding angle and reset 控制步进电机转动到对应角度并复位
        motor = StepperMotorController()
        motor.rotate(model) # rotate是类方法，不是模块直接属性，所以要用这种方式调用（from……import）

    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    main()
