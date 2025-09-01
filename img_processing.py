import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import sensors


"""
————————————————————————————————————————————————————————————————————————————————————————————————————————

图像处理函数：
收到来自于camera拍摄的照片后，进行处理
得出直径和长度（单位为像素）

-------------------------------------------

Image processing function:
After receiving a photo from the camera, process it and obtain the diameter and length (in pixels).


——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""


def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2,2))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=12)
    return opened

def largest_contour(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    return max(contours, key=cv2.contourArea)

def min_rect(contour, pixel_to_mm=1.0):
    # 获得最小外接矩形
    rect = cv2.minAreaRect(contour)
    (cx, cy), (w, h), angle = rect

    # 保证w >= h
    if h > w:
        w, h = h, w
        angle += 90

    w_mm = w * pixel_to_mm
    h_mm = h * pixel_to_mm

    # 简单分类依据：螺母宽高比接近1（0.8~1.2）判为螺母 否则螺丝
    aspect = w / h if h != 0 else 0
    if 0.8 <= aspect <= 1.2:
        part_type = 'nut'
    else:
        part_type = 'screw'

    return {
        'part_type': part_type,
        'length_px': w,
        'diameter_px': h,
        'length_mm': w_mm,
        'diameter_mm': h_mm,
        'center': (cx, cy),
        'angle': angle,
        'aspect_ratio': aspect
    }


def img_recog(image_path, roi, pixel_to_mm=0.035):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to read image at {image_path}")
   
    x, y, w, h = roi
    img_crop = img[y:y+h, x:x+w]

    mask = preprocess(img_crop)
    contour = largest_contour(mask)
    if contour is None:
        raise ValueError('No contour detected!')

    result = min_rect(contour, pixel_to_mm)



    return result