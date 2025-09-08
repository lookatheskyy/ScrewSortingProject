# conveyorbelt.py
import time
import RPi.GPIO as GPIO
import threading




# 1号L298N驱动板控制a传送带的电机（电机2号）
# GPIO引脚定义，根据实际硬件接线修改
A_IN3_PIN = 22  # a传送带电机控制引脚1（正转）
A_IN4_PIN = 23  # a传送带电机控制引脚2（反转）

# 2号L298N驱动板控制b传送带的电机（电机3号）
B_IN1_PIN =24   # b传送带电机控制引脚1（正转）
B_IN2_PIN =25   # b传送带电机控制引脚2（反转）

# 初始化GPIO模式为BCM编号方式，关闭警告
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 设置传送带两个电机的控制引脚为输出模式
GPIO.setup(A_IN3_PIN, GPIO.OUT)
GPIO.setup(A_IN4_PIN, GPIO.OUT)
GPIO.setup(B_IN1_PIN, GPIO.OUT)
GPIO.setup(B_IN2_PIN, GPIO.OUT)

# 标记a和b传送带是否运行状态
_a_running = False
_b_running = False

"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

传送带启停函数：
def start_conveyorbelt: 通电后立即启动
def stop_conveyorbelt ：传送带停止（检测到物体后）
def restart_conveyorbelt ： 步进电机旋转到位停止5s左右后，重启

触发动作由主程序提供


stop_conveyorbelt函数的参数：sensors()
restart_conveyorbelt函数的参数：stepper_motor()


——————————————————————————————————————————————————————————————————————————————————————————————————————————
ENG Version:
Call by main program

"""


def _start_short():
    """
    启动a传送带电机（正转）
    输出高低电平使电机正转，开始运行
    """
    global _a_running
    GPIO.output(A_IN3_PIN, GPIO.HIGH)
    GPIO.output(A_IN4_PIN, GPIO.LOW)
    _a_running = True
    print("Conveyor belt A started.")

def _stop_short():
    """
    停止a传送带电机
    输出低电平使电机停止
    """
    global _a_running
    GPIO.output(A_IN3_PIN, GPIO.LOW)
    GPIO.output(A_IN4_PIN, GPIO.LOW)
    _a_running = False
    print("Conveyor belt A stopped.")

def _start_long():
    """
    启动b传送带电机（正转）
    输出高低电平使电机正转，开始运行
    """
    global _b_running
    GPIO.output(B_IN1_PIN, GPIO.HIGH)
    GPIO.output(B_IN2_PIN, GPIO.LOW)
    _b_running = True
    print("Conveyor belt B started.")

def _stop_long():
    """
    停止b传送带电机
    输出低电平使电机停止
    """
    global _b_running
    GPIO.output(B_IN1_PIN, GPIO.LOW)
    GPIO.output(B_IN2_PIN, GPIO.LOW)
    _b_running = False
    print("Conveyor belt B stopped.")

def conveyorbelt_start():
    """
    外部调用接口：同时启动a和b两个传送带
    """
    _start_short()
    _start_long()

def conveyorbelt_stop():
    """
    外部调用接口：同时停止a和b传送带
    """
    _stop_short()
    _stop_long()


