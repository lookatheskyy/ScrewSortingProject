import time
#import RPi.GPIO as GPIO  ubuntu下安装
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os




"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

传送带启停函数：
def start_converyorbelt:通电后立即启动
def converyorbelt_stop ：传送带停止（检测到物体后）
converyorbelt_restart ： 步进电机旋转到位停止5s左右后，重启

触发动作由主程序提供


converyorbelt_stop函数的参数：sensors()
converyorbelt_restart函数的参数：stepper_motor()

注意：zqd有点分不清哪些功能是在模块里面写，哪些动作是由主程序调动了
多捋逻辑关系，工作流程（主程序里有些），然后和zqd讨论
各个模块的参数命名需要统一，避免传参失败。
各个模块的功能串联zqd认为很麻烦很繁琐，应积极讨论
——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""

def start_converyorbelt()

def stop_conveyorbelt()

def restart_conveyorbelt()