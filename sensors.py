import time
#import RPi.GPIO as GPIO  
import cv2
import numpy as np
import os
import conveyorbelt
import img_processing


"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

红外线传感器函数：
用于检测物体是否出现在camera下方。
若出现，则传送带停止。

-------------------------------------------

Infrared sensor function:
Used to detect whether an object appears under the camera.
If so, the conveyor stops.

——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""




class InfraredSensor:
    def __init__(self, sensor_pin=16, poll_interval=0.1):  # sensor_pin=16 改为实际分配给红外传感器的GPIO口
        self.sensor_pin = sensor_pin
        self.poll_interval = poll_interval  # 传感器检测轮询时间(秒)

        # GPIO 初始化
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sensor_pin, GPIO.IN)

    def wait_for_object(self):
        """
        等待红外传感器检测到物体（假设检测到时GPIO为HIGH）。
        返回后，开始处理流程。
        """
        print("等待红外传感器检测物体...")
        try:
            while True:
                sensor_state = GPIO.input(self.sensor_pin)
                if sensor_state == GPIO.HIGH:
                    print("检测到目标物体！")
                    return True
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("检测中断，清理GPIO资源")
            GPIO.cleanup()
            return False

    def run(self):
        try:
            while True:
                detected = self.wait_for_object()
                if detected:
                    # 1 停止传送带
                    conveyorbelt.stop_conveyor()
                    # 2 环形灯常亮
                    conveyorbelt.turn_on_ring_light()
                    # 3 摄像头拍照并图像识别
                    img_processing.capture_and_process_image()
                    # 4 处理完成，关闭环形灯，启动传送带
                    conveyorbelt.turn_off_ring_light()
                    conveyorbelt.start_conveyor()
                    print("处理完成，等待下一次检测。")
                    # 可适当延时，防止误检
                    time.sleep(1)
        finally:
            GPIO.cleanup()
            print("GPIO清理完毕，程序退出。")


if __name__ == "__main__":
    sensor = InfraredSensor(sensor_pin=16)
    sensor.run()