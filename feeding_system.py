# feeding_system.py

import time  
import RPi.GPIO as GPIO

"""
————————————————————————————————————————————————————————————————————————————————————————————————————————


feeding_system
Control the start and stop of the motor. The specific triggering action is provided by the main program.
trigger feeding_system
call by main program

——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""



# No. 1 L298N driver board controls motor No. 1 (feeding system motor)
A_IN1_PIN = 17  
A_IN2_PIN = 27  

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO.setup(A_IN1_PIN, GPIO.OUT)
GPIO.setup(A_IN2_PIN, GPIO.OUT)


_running = False






def _motor_start():
    """
    Feeding system motor start function (forward rotation)
    Set IN1 high and IN2 low to drive the motor forward.
    """
    GPIO.output(A_IN1_PIN, GPIO.HIGH)
    GPIO.output(A_IN2_PIN, GPIO.LOW)
    global _running
    _running = True
    print("Feeding system motor started.")
    
    

def _motor_stop():
    """
    Feeding system motor stop function: Make both control pins output low level, and the motor stops.
    """
    GPIO.output(A_IN1_PIN, GPIO.LOW)
    GPIO.output(A_IN2_PIN, GPIO.LOW)
    global _running
    _running = False
    print("Feeding system motor stopped.")


def feedingsystem_start():
  
    _motor_start()

def feedingsystem_stop():
   
    _motor_stop()

