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

from feeding_system import feedingsystem_start, feedingsystem_stop, feedingsystem_restart
from conveyorbelt import conveyorbelt_start, conveyorbelt_stop, conveyorbelt_restart_1



"""
————————————————————————————————————————————————————————————————————————————————————————————————————————


控制流程
step 1 ：通电后自动启动：进料系统的电机、传送带电机、环形灯、传感器→ 
step 2 ：送入目标检测物 →
step 3 ：传感器检测到物体→ 
step 4 ：进料系统与传送带停止→ 
step 5 ：获取照片并进行图像处理→ 
step 6 ：分类并获得分类结果→ 
step 7 ：步进电机启动（3秒后复位）→ 
step 8 ：长传送带启动（1秒后停止）→ 
step 9 ：进料系统与传送带系统启动→
step 10 ：回到第二步


-------------------------------------------
English：
Control Flow

——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""

RING_LIGHT_PIN = 18  # 假设环形灯用GPIO18 
LED_COUNT = 16
LED_FREQ_HZ = 800000
LED_DMA = 10              # DMA通道
LED_INVERT = False        # 是否反转信号
LED_BRIGHTNESS = 10



class RingLight:
    def __init__(self, count=LED_COUNT, pin=RING_LIGHT_PIN, brightness=LED_BRIGHTNESS):
        self.led_count = count
        self.strip = PixelStrip(count, pin, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
        self.strip.begin()
    
    def turn_on(self, color=Color(255, 255, 255)):
        """全部灯珠点亮指定颜色，默认为白色"""
        for i in range(self.led_count):
            self.strip.setPixelColor(i, color)
        self.strip.show()
        print("Ring light turned on.")
        
    def turn_off(self):
        """全部灯珠关闭"""
        for i in range(self.led_count):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        self.strip.show()
        print("Ring light turned off.")
        



def main():
    
    
    GPIO.setmode(GPIO.BCM)
    
    
    # 初始化设备
    sensor = sensors.InfraredSensor()
    ring_light = RingLight()
    
    roi = (2, 395, 1911, 280)
    pixel_to_mm = 0.05



    try:
        # step 1: 启动进料电机、传送带、环形灯，传感器GPIO已初始化
        feedingsystem_start()
        conveyorbelt_start()
        ring_light.turn_on()
        
    
        while True:
            print("等待检测到物体...")
            
            # step 2 & 3 & 4：循环判断传感器是否检测到物体，检测到则停止传送带和进料
            while True:
                if sensor.is_object_detected():
                    print("检测到物体，停止进料和传送带")
                    conveyorbelt_stop()
                    feedingsystem_stop()
                    break
                else:
                    conveyorbelt_start()
                    feedingsystem_start()
                time.sleep(0.1)
        
            # step 5： Take a picture and save it 拍摄图片并保存 
            image_path = camera.capture_image()
            print(f"Image captured and saved to {image_path}")

            # step 6： Read the image and detect 读取图片并检测
            result = img_processing.img_recog(image_path, roi, pixel_to_mm)
            print('Detection result:')
            print(f"Part type: {result['part_type']}")
            print(f"Length: {result['length_px']:.1f} px / {result['length_mm']:.2f} mm")
            print(f"Diameter: {result['diameter_px']:.1f} px / {result['diameter_mm']:.2f} mm")
            print(f"Angle: {result['angle']:.1f} degrees")
            print(f"Aspect ratio: {result['aspect_ratio']:.2f}")

            #  Classify 进行型号分类
            model = classification.classify_model(result)
            print(f'Matched Model: {model}')

            # step 7： Control the stepper motor to rotate to the corresponding angle and reset 控制步进电机转动到对应角度并复位
            motor = StepperMotorController()
            motor.rotate(model) # rotate是类方法，不是模块直接属性，所以要用这种方式调用（from……import）
         
            # step 8
            # 先只启动长传送带，1s后停止
            conveyorbelt._start_long()  # 直接调用模块中私有函数
            time.sleep(1)
            conveyorbelt._stop_long()
            
            time.sleep(5)
            motor.reset(model)
            # 再同时启动进料与传送带，开启下一轮识别
            feedingsystem_start()
            conveyorbelt_start()
            
            # step 10 循环回去等待传感器检测..
            
            
    except Exception as e:
        print('Error:', e)

if __name__ == '__main__':
    main()
