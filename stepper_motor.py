import time
import RPi.GPIO as GPIO  


"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

步进电机函数：启动和复位

参数：classification.py
（无法判断螺丝是否已经滑落至指定盒子，所以当收到分类结果信号，转到指定的位置后，自动复位）

分类模块输出结果：10类
nut_M4
nut_M6
nut_M8
screw_M4-20
screw_M4-40
screw_M6-20
screw_M6-40
screw_M8-20
screw_M8-40
other

步进电机型号：lema17，驱动板a4988
控制逻辑：
DIR = 0/1 控制电机旋转方向
STEP 从低到高的一个脉冲使电机转动一步，步进角比如1.8°对应200步/转（100μ步）
转动指定角度：计算步数＝(角度/步进角度)*细分系数

-------------------------------------------
English:
Stepper Motor Function: Start and Reset

Parameters: classification.py
(It cannot determine whether the screw has already fallen into the designated box, so it automatically resets after receiving the classification result signal and moving to the designated position.)

Classification module output: 10 categories
nut_M4
nut_M6
nut_M8
screw_M4-20
screw_M4-40
screw_M6-20
screw_M6-40
screw_M8-20
screw_M8-40
other

Stepper motor model: lema17, driver board a4988
Control logic:
DIR = 0/1 controls the motor's rotation direction
STEP: A pulse from low to high causes the motor to rotate one step. For example, a step angle of 1.8° corresponds to 200 steps/revolution (100 μ steps).
To rotate a specified angle: Calculate the number of steps = (angle / step angle) * subdivision factor


——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""
class StepperMotorController:
    def __init__(self, dir_pin=21, step_pin=20,
                 step_angle=1.8, microstep=1, step_delay=0.01):

        self.DIR = dir_pin
        self.STEP = step_pin
        self.STEP_ANGLE = step_angle
        self.MICROSTEP = microstep
        self.STEP_DELAY = step_delay

        self.STEPS_PER_REV = int(360 / self.STEP_ANGLE * self.MICROSTEP)

         # # Corresponding angles for 10 categories 10类对应角度
        self.category_angle_map = {
            "M4": 0,
            "M6": 36,
            "M8": 72,
            "M4_20": 108,
            "M4_40": 144,
            "M6_20": 180,
            "M6_40": 216,
            "M8_20": 252,
            "M8_40": 288,
            "Unknown Model": 324
        }

        # Initialize GPIO 初始化GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DIR, GPIO.OUT)
        GPIO.setup(self.STEP, GPIO.OUT)
        
        
        # Fixed direction is high level 固定方向为高电平，如需改成低电平修改下面一行
        GPIO.output(self.DIR, GPIO.LOW)

    def angle_to_steps(self, angle):
        """Angle to step conversion 角度转为步数"""
        return int(self.STEPS_PER_REV * angle / 360)
    
    def step_motor(self, steps):
        """The stepper motor rotates, and the number of steps must be positive.
        步进电机转动，steps必须正数"""
        
        for _ in range(steps):
            GPIO.output(self.STEP, GPIO.HIGH)
            time.sleep(self.STEP_DELAY)
            GPIO.output(self.STEP, GPIO.LOW)
            time.sleep(self.STEP_DELAY)
            
    def rotate(self, category):
        category = category if category in self.category_angle_map else 'other'
        angle = self.category_angle_map[category]
        steps_move = self.angle_to_steps(angle)
        

        print(f"[Motor Control电机控制] category类别: {category}, Steering angle转向角度: {angle}°, Rotation steps转动步数: {steps_move}")
        self.step_motor(steps_move)
        
    def reset(self, category):
        category = category if category in self.category_angle_map else 'other'
        angle = self.category_angle_map[category]
        steps_move = self.angle_to_steps(angle)
        steps_reset = self.STEPS_PER_REV - steps_move  
        
        print("[Motor Control电机控制] Reset复位,Steps步数:", steps_reset)
        self.step_motor(steps_reset)
        print("[Motor Control电机控制] Reset completed复位完成\n")

