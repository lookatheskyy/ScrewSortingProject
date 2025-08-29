import time
#import RPi.GPIO as GPIO  
import cv2
import numpy as np
import os
import classification

"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

步进电机函数：启动和复位

参数：classification.py
（无法判断螺丝是否已经滑落至指定盒子，所以当收到分类结果信号，转到指定的位置后，设置一个time停5秒左右，然后复位）

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

——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""

def stepper()