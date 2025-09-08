# feeding_system.py

import time  
import RPi.GPIO as GPIO



# 引脚定义（可根据实际接线调整）
# 1号L298N驱动板控制电机1号（进料系统电机）
A_IN1_PIN = 17  # 电机控制引脚1
A_IN2_PIN = 27  # 电机控制引脚2
# 初始化GPIO模式为BCM编号方式，关闭警告
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 设置电机控制引脚为输出模式
GPIO.setup(A_IN1_PIN, GPIO.OUT)
GPIO.setup(A_IN2_PIN, GPIO.OUT)

# 变量标识电机是否处于运行状态
_running = False


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




def _motor_start():
    """
    进料系统电机启动函数（正转）
    使IN1高电平，IN2低电平，驱动电机正向旋转
    """
    GPIO.output(A_IN1_PIN, GPIO.HIGH)
    GPIO.output(A_IN2_PIN, GPIO.LOW)
    global _running
    _running = True
    print("Feeding system motor started.")
    
    

def _motor_stop():
    """
    进料系统电机停止函数
    使两个控制引脚均输出低电平，电机停止
    """
    GPIO.output(A_IN1_PIN, GPIO.LOW)
    GPIO.output(A_IN2_PIN, GPIO.LOW)
    global _running
    _running = False
    print("Feeding system motor stopped.")


def feedingsystem_start():
    """
    外部调用接口：启动进料系统电机
    """
    _motor_start()

def feedingsystem_stop():
    """
    外部调用接口：停止进料系统电机
    """
    _motor_stop()

