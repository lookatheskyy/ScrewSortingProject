# conveyorbelt.py
import time
import RPi.GPIO as GPIO


CONVEYOR_MOTOR_PIN = 12
RING_LIGHT_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(CONVEYOR_MOTOR_PIN, GPIO.OUT)
GPIO.setup(RING_LIGHT_PIN, GPIO.OUT)

"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

传送带启停函数：
def start_conveyorbelt:通电后立即启动
def stop_conveyorbelt ：传送带停止（检测到物体后）
def restart_conveyorbelt ： 步进电机旋转到位停止5s左右后，重启

触发动作由主程序提供


stop_conveyorbelt函数的参数：sensors()
restart_conveyorbelt函数的参数：stepper_motor()

注意：zqd有点分不清哪些功能是在模块里面写，哪些动作是由主程序调动了
多捋逻辑关系，工作流程（主程序里有些），然后和zqd讨论
各个模块的参数命名需要统一，避免传参失败。
各个模块的功能串联zqd认为很麻烦很繁琐，应积极讨论
——————————————————————————————————————————————————————————————————————————————————————————————————————————
ENG Version:
Call by main program

"""

def start_conveyorbelt():
    """启动传送带电机"""
    GPIO.output(CONVEYOR_MOTOR_PIN, GPIO.HIGH)
    print("Conveyor belt started.")

def stop_conveyorbelt():
    """停止传送带"""
    GPIO.output(CONVEYOR_MOTOR_PIN, GPIO.LOW)
    print("Conveyor belt stopped.")

def restart_conveyorbelt(delay=0):
    """
    重新启动传送带
    delay: 延时时间，通常步进电机归位后才调用，可选
    eng version: Restart the conveyor belt

    """
    if delay > 0:
        time.sleep(delay)
    GPIO.output(CONVEYOR_MOTOR_PIN, GPIO.HIGH)
    print("Conveyor belt restarted.")

def turn_on_ring_light():
    """开启环形灯
    eng version: Turn on the ring light
    """
    GPIO.output(RING_LIGHT_PIN, GPIO.HIGH)
    print("Ring light turned ON.")

def turn_off_ring_light():
    """关闭环形灯
    eng version: Turn off the ring light
    """
    GPIO.output(RING_LIGHT_PIN, GPIO.LOW)
    print("Ring light turned OFF.")

def cleanup():
    """清理GPIO设置
    eng version: Clean up GPIO settings
    """
    GPIO.output(CONVEYOR_MOTOR_PIN, GPIO.LOW)
    GPIO.output(RING_LIGHT_PIN, GPIO.LOW)
    GPIO.cleanup()