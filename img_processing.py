import time
import cv2
import numpy as np

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


def preprocess(img, save_steps=True, output_dir="debug_steps", base_name='1'):
    """
    Image Preprocessing
    将原始图像转换成干净且容易提取轮廓的二值图像
    
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 灰度转换
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))  #增强对比度
    gray_clahe = clahe.apply(gray)  #增强对比度
    gray_blur = cv2.medianBlur(gray_clahe, 5)  # 中值模糊滤波
    if save_steps and output_dir:
        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_gray.png"), gray)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)   # 阈值二值化（OSTU）
    if save_steps and output_dir:
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_thresh.png"), thresh)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=10)   # 形态学闭运算和开运算去噪
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)
    if save_steps and output_dir:
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_closed.png"), closed)
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_opened.png"), opened)  
    return opened



"""
Object Detection & Measurement

"""

# 从二值图像中找出所有轮廓，返回面积最大的轮廓，作为目标检测物的轮廓
def largest_contour(mask):   
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    return max(contours, key=cv2.contourArea)

# 计算目标轮廓的最小外接矩形 
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

 # 裁剪ROI,调用上面两个函数。
def img_recog(image_path, roi, pixel_to_mm=0.035, save_steps=True, output_dir="debug_steps"):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to read image at {image_path}")
   
    x, y, w, h = roi
    img_crop = img[y:y+h, x:x+w]
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    roi_tag = f"{base_name}_roi_{x}_{y}_{w}_{h}"
    

    # 保存裁剪的 ROI（原图裁剪）
    if save_steps and output_dir:
        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(os.path.join(output_dir, f"{roi_tag}_orig.png"), img_crop)

    mask = preprocess(img_crop, save_steps=save_steps, output_dir=output_dir, base_name=roi_tag)
    contour = largest_contour(mask)
    if contour is None:
        raise ValueError('No contour detected!')

    result = min_rect(contour, pixel_to_mm)

    # 保存带注释的可视化结果
    if save_steps and output_dir:
        annotated = img_crop.copy()
        # 轮廓（红色）
        cv2.drawContours(annotated, [contour], -1, (0,0,255), 2)

        # 最小外接矩形（绿色）
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(annotated, [box], 0, (0,255,0), 2)

        # 中心点（蓝色小圆点）
        cx, cy = int(result['center'][0]), int(result['center'][1])
        cv2.circle(annotated, (cx, cy), 4, (255,0,0), -1)

        # 文本信息
        text = f"{result['part_type']} L_px:{int(result['length_px'])} D_px:{int(result['diameter_px'])}"
        cv2.putText(annotated, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        cv2.imwrite(os.path.join(output_dir, f"{roi_tag}_annotated.png"), annotated)
        # 也保存最终的 mask 便于排查
        cv2.imwrite(os.path.join(output_dir, f"{roi_tag}_mask.png"), mask)

    return result

