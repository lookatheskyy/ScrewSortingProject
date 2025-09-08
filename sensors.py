import time
import RPi.GPIO as GPIO  




"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

红外线传感器函数：
检测数字高低电平即可判断是否检测到物体。

型号：MH-Sensor-series Flying flash
一般会有一个阈值电压用来判断“检测到物体”与否

GPIO接线：
VCC接3.3V或5V（建议5V供电，模块有稳压）
GND接树莓派GND
OUT接树莓派GPIO输入口，如GPIO17（BCM编号）
-------------------------------------------



——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""


# 假设红外传感器输出接在GPIO17
SENSOR_PIN = 16

class InfraredSensor:
    def __init__(self, pin=SENSOR_PIN):
        self.pin = pin   # 传感器连接的GPIO口号，例如GPIO17
        self.object_detected = False   # 变量，当前是否检测到物体，初始为未检测

        GPIO.setmode(GPIO.BCM)      # 使用BCM编号
        GPIO.setup(self.pin, GPIO.IN)   # 设置该引脚为输入模式

        # 注册GPIO事件检测（检测GPIO电平变化时调用回调函数）
        # 监听引脚电平的上升沿或下降沿 (GPIO.BOTH)，防抖时间200ms
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self._sensor_callback, bouncetime=200)

    def _sensor_callback(self, channel):
        """
        这是事件检测触发时调用的回调函数，
        参数channel是触发的GPIO引脚编号（这里就是self.pin）。
        """
        level = GPIO.input(self.pin)
        # 根据检测到的电平判定是否有物体
        # 低电平（0）表示检测到物体，高电平（1）表示无物体
        if level == 0:   # 已用万用表检测到：低电平表示有物体
            self.object_detected = True
        else:
            self.object_detected = False

    def is_object_detected(self):
        """
        外部查询接口，返回当前是否检测到物体的状态
        """
        return self.object_detected

   


# 测试代码
if __name__ == "__main__":
    
    sensor = InfraredSensor(SENSOR_PIN)
    try:
        while True:
            if sensor.is_object_detected():
                print("检测到物体！")
            else:
                print("未检测到物体")
            time.sleep(0.1)
    except KeyboardInterrupt:
        sensor.cleanup()