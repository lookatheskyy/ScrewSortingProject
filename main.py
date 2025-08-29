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
    ring_light = RingLight(pin=18)
    ir_sensor = sensors.InfraredSensor(sensor_pin=16)

    try:
        print("启动环形灯 常亮中...")
        ring_light.turn_on()
        
        print("启动传送带，开始输送")
        conveyorbelt.start_conveyor()

        print("开始传感器检测物体")
        while True:
            
            if ir_sensor.wait_for_detection():
                
                
                
                conveyorbelt.stop_conveyorbelt()
                print("检测到物体，停止传送带。")
                
                
                
                
                image_path = img_processing.capture_image()
                print(f"拍照完成，图片存储于：{image_path}")




                # 将路径传递给图像处理函数（字典）
                size_dict = img_processing.img_processing(image_path)   
                # 例如 {'part_type': 'nut', 'diameter': 40} 或 {'part_type': 'screw', 'diameter': 5, 'length': 20}
                print(f"图像处理结果：{size_dict}")




                # 根据图像处理结果调用分类模块
                part_type = size_dict.get('part_type')
                if part_type == 'nut':
                    size_info = size_dict.get('diameter')
                elif part_type == 'screw':
                    diameter = size_dict.get('diameter')
                    length = size_dict.get('length', None)
                    if length is not None:
                        size_info = (diameter, length)
                    else:
                        size_info = (diameter, 0)
                else:
                    size_info = None

                class_result = classification.classification(part_type, size_info)
                print(f"分类结果：{class_result}")




                # 调用步进电机定位，传入分类结果，传送带重启  这里的命名需修改为定义的，保证接口一致，传参成功
                stepper_motor.move_to_position(class_result)
                print("步进电机定位完成，传送带重新启动...")
                conveyorbelt.restart_conveyorbelt()



                time.sleep(0.5)  # 防止误判
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("用户手动终止程序")
    finally:
        ring_light.cleanup()
        ir_sensor.cleanup()
        conveyorbelt.stop_conveyor()
        print("资源已清理，设备安全关闭")

if __name__ == "__main__":
    main()