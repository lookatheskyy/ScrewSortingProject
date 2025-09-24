import time
import RPi.GPIO as GPIO  


"""
————————————————————————————————————————————————————————————————————————————————————————————————————————


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

         # # Corresponding angles for 10 categories 
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

        # Initialize GPIO 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DIR, GPIO.OUT)
        GPIO.setup(self.STEP, GPIO.OUT)
        
        
        # Fixed direction is high level 
        GPIO.output(self.DIR, GPIO.LOW)

    def angle_to_steps(self, angle):
        """Angle to step conversion """
        return int(self.STEPS_PER_REV * angle / 360)
    
    def step_motor(self, steps):
        """The stepper motor rotates, and the number of steps must be positive.
        """
        
        for _ in range(steps):
            GPIO.output(self.STEP, GPIO.HIGH)
            time.sleep(self.STEP_DELAY)
            GPIO.output(self.STEP, GPIO.LOW)
            time.sleep(self.STEP_DELAY)
            
    def rotate(self, category):
        category = category if category in self.category_angle_map else 'other'
        angle = self.category_angle_map[category]
        steps_move = self.angle_to_steps(angle)
        

        print(f"[Motor Control] category: {category}, Steering angle: {angle}°, Rotation steps: {steps_move}")
        self.step_motor(steps_move)
        
    def reset(self, category):
        category = category if category in self.category_angle_map else 'other'
        angle = self.category_angle_map[category]
        steps_move = self.angle_to_steps(angle)
        steps_reset = self.STEPS_PER_REV - steps_move  
        
        print("[Motor Control] Reset,Steps:", steps_reset)
        self.step_motor(steps_reset)
        print("[Motor Control] Reset completed\n")

