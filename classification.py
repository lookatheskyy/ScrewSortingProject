import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os



"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

分类函数：
根据图像处理结果进行分类判定
输出结果：
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

-------------------------------------------

Classification function:
Classification is determined based on the image processing results
Output result:
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

def classification(part_type, size_info):
    
    """
    分类螺丝或螺母

    参数:
        part_type(str): 'nut' 或 'screw'
        size_info: 
            如果 part_type == 'nut'，是直径像素 (float)
            如果 part_type == 'screw'，是 (直径像素, 长度像素) 元组 (float, float)
    返回:
        分类字符串，如'M4-20', 'M6', 'Unknown'等
    """
    # 阈值区间，根据实际标定数据调整
    # 像素与毫米的对应比例是线性的：
    # M4直径=40mm  对应直径像素区间 (35 ~ 45) 后面根据实际测试出来的像素进行修改
    # M6直径=60mm  对应直径像素区间 (55 ~ 65)
    # M8直径=80mm  对应直径像素区间 (75 ~ 85)

 
 
    # 定义阈值字典
    diam_thresholds = {
        'M4': (35, 45),
        'M6': (55, 65),
        'M8': (75, 85),
    }
    length_thresholds = {
        20: (18, 22),  # 20mm长度对应的像素区间
        40: (38, 42),  # 40mm长度对应的像素区间
    }
    # 定义判断函数：判断给定的数值value是否在区间range_tuple内
    def check_in_range(value, value_range):
        return value_range[0] <= value <= value_range[1]



    # 螺母的分类处理
    if part_type == 'nut':
        diameter_px = size_info
        if diameter_px is None:
            return "Unknown Nut (No diameter)"

        for key, (low, high) in diam_thresholds.items(): # 遍历螺母的直径阈值字典，依次判断在哪个区间里
            if check_in_range(diameter_px, (low, high)):
                return f"nut_{key}"   # 找到，就返回该规格名称，如 nut_M4
        return "other"    # 遍历后没有，则返回 其他类
    
    
    
    
    # 螺丝的分类处理
    elif part_type == 'screw':
        if not isinstance(size_info, tuple) or len(size_info) != 2: # 若为螺丝，需要传入一个元组，包含直径和长度两个值
            return "other"       # 若传入格式不是元素或长度不等于2，就返回错误信息
        diameter_px, length_px = size_info   # 拆出直径和长度两个像素值

        screw_key = None
        for key, (low, high) in diam_thresholds.items():   # 遍历直径阈值字典
            if check_in_range(diameter_px, (low, high)):
                screw_key = key
                break
        if not screw_key:
            return "other"  # 直径遍历后没有，则返回 其他类
        
        length_key = None  
        for length_mm, (low, high) in length_thresholds.items():  # 遍历长度阈值字典
            if check_in_range(length_px, (low, high)):
                length_key = length_mm
                break
        if not length_key:
            return f"{screw_key}-other"  # 长度遍历后没有，则返回直径**，长度其他（这里没有直接归为other类，是在考虑错误率是否太高，留一点空间降低错误率至少保证直径是对的）
        return f"screw_{screw_key}-{length_key}"  # 返回完整规格名 screw_M4-20

    else:
        return "other"  # 若传入的不是nut也不是screws，则返回 其他类
 
 
 
 
 
 
 
 
 
 
 
 
 