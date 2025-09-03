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

def classify_model(detection_result):
    """
    根据检测结果字典，判断具体型号。
    使用尺寸范围字典区间匹配。
    
    """

    part_type = detection_result.get('part_type')
    length = detection_result.get('length_mm')
    diameter = detection_result.get('diameter_mm')

    # Define model determination dictionary 定义型号判定字典
    model_dict = {
        'screw': [
            {'model': 'M8_20', 'diameter_range': (11, 14), 'length_range': (25, 28)},
            {'model': 'M8_40', 'diameter_range': (11, 14), 'length_range': (45, 48)},
            {'model': 'M6_20', 'diameter_range': (9, 11), 'length_range': (22, 26)},
            {'model': 'M6_40', 'diameter_range': (9, 11), 'length_range': (42, 46)},
            {'model': 'M4_20', 'diameter_range': (6, 9), 'length_range': (22, 24)},
            {'model': 'M4_40', 'diameter_range': (6, 9), 'length_range': (42, 44)},
        ],
        'nut': [
            {'model': 'M8', 'diameter_range': (12.01, 15), 'length_range': (12.01, 15)},
            {'model': 'M6', 'diameter_range': (10, 12), 'length_range': (10, 12)},
            {'model': 'M4', 'diameter_range': (7, 8), 'length_range': (7, 8)},
        ]
    }

    if part_type not in model_dict:
        return 'Unknown Part Type'

    candidates = model_dict[part_type]

    for item in candidates:
        h_min, h_max = item['diameter_range']
        w_min, w_max = item['length_range']
        if h_min <= diameter <= h_max and w_min <= length <= w_max:
            return item['model']

    return 'Unknown Model'
