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


def capture_image(save_path='/home/pi/images', camera_index=0, width=1920, height=1080, fps=30):
    """
    使用USB摄像头捕获一张照片，可以设置分辨率和帧率。

    参数：
    - save_path: 图片保存目录
    - camera_index: 摄像头ID，一般默认0
    - width, height: 分辨率
    - fps: 帧率

    返回：
    - 保存的图片路径
    """
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("无法打开USB摄像头")

    # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # 设置帧率
    cap.set(cv2.CAP_PROP_FPS, fps)

    # 预热摄像头，读取多帧稳定曝光等设置
    for _ in range(30):
        ret, frame = cap.read()
        if not ret:
            raise RuntimeError("摄像头读取失败")
        time.sleep(0.05)

    # 真正采集一张清晰的照片
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("摄像头采集图像失败")

    # 确保保存路径存在
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 生成文件名，按时间戳
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    img_file = os.path.join(save_path, f'image_{timestamp}.jpg')

    # 保存图片
    cv2.imwrite(img_file, frame)

    # 释放摄像头资源
    cap.release()

    return img_file






img_path = r'C:\pic\img23.jpg'

def img_processing(img_path):
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Failed to read image: {img_path}")

    # 转HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 设置绿色背景阈值，后期根据实际调整
    lower_black = np.array([35, 50, 50])
    upper_black = np.array([185, 255, 255])
    # 根据背景生成背景掩膜
    background_mask = cv2.inRange(hsv, lower_black, upper_black)
    # 反转掩膜得到螺栓掩膜
    screw_mask = cv2.bitwise_not(background_mask)
    # 对掩膜进行形态学清理，去除噪声
    kernel = np.ones((1, 1), np.uint8)  # 创建一个1*1的核，噪声大时增大核尺寸
    # 闭运算 + 开运算
    screw_mask_cleaned = cv2.morphologyEx(screw_mask, cv2.MORPH_CLOSE, kernel)
    screw_mask_cleaned = cv2.morphologyEx(screw_mask_cleaned, cv2.MORPH_OPEN, kernel)
    # 获取最大轮廓：假设最大的黑色区域就是螺栓
    contours, _ = cv2.findContours(screw_mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("未检测到任何轮廓 No contours detected")
    screw_contour = max(contours, key=cv2.contourArea)

    height, width = img.shape[:2]
    aspect_ratio = width / height
    is_nut = (0.8 <= aspect_ratio <= 1.2)  # 判定阈值可调整



    if is_nut:
        print("判断为螺母 (Nut) — 长宽比接近1.Identified as a nut (Nut) — the aspect ratio is close to 1")
        contours, _ = cv2.findContours(screw_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return{'part_type': 'nut', 'diameter': None}
        nut_contour = max(contours, key=cv2.contourArea)
        # 计算最小外接圆直径
        (x, y), radius = cv2.minEnclosingCircle(nut_contour)
        diameter_circle = 2 * radius
        # 计算最小外接矩形长边
        rect = cv2.minAreaRect(nut_contour)
        width_rect, height_rect = rect[1]
        diameter_rect = max(width_rect, height_rect)
        nut_diameter = max(diameter_circle, diameter_rect)
        return {'part_type': 'nut', 'diameter': nut_diameter}


    # -----螺丝长度的判定代码，还需要继续修改---------------------------------------------------------
    else:
        # 获取主方向矩形信息
        rect = cv2.minAreaRect(screw_contour)
        center, (w, h), angle = rect
        # 取长边方向作为主轴向量
        if w > h:
            length_long = w
            length_short = h
            angle_long_axis = angle  # 角度范围(-90,0],长边对应角度
        else:
            length_long = h
            length_short = w
            angle_long_axis = angle + 90  # 调整为长边方向角度

        # 将角度转换为弧度
        theta = np.deg2rad(angle_long_axis)
        # 主轴单位向量（长边方向）
        axis_long = np.array([np.cos(theta), np.sin(theta)])
        # 垂直主轴单位向量（宽度方向）
        axis_short = np.array([-axis_long[1], axis_long[0]])

        # 螺丝轮廓点
        contour_pts = screw_contour[:, 0, :]  # shape(N,2)

        # 轮廓点相对于中心的向量
        vec_pts = contour_pts - center

        # 轮廓点在主轴上的投影坐标（标量）
        proj_long = vec_pts @ axis_long  # 点乘，得到标量投影值

        # 轮廓点在垂直轴上的投影坐标（宽度方向投影）
        proj_short = vec_pts @ axis_short

        # 依据主轴投影坐标选头部和杆部，假设头部在长轴大投影端
        proj_min = proj_long.min()
        proj_max = proj_long.max()
        length_total = proj_max - proj_min

        # 经验头部长度占比25%
        head_ratio = 0.25
        head_threshold = proj_max - length_total * head_ratio

        # 头部点： 主轴投影 >= head_threshold
        head_mask = proj_long >= head_threshold
        head_proj_short = proj_short[head_mask]

        # 杆部点： 主轴投影 < head_threshold
        shaft_mask = proj_long < head_threshold
        shaft_proj_long = proj_long[shaft_mask]

        if head_proj_short.size > 0:
            head_width = head_proj_short.max() - head_proj_short.min()
        else:
            head_width = 0
            

        if shaft_proj_long.size > 0:
            shaft_length = head_threshold - shaft_proj_long.min()
        else:
            shaft_length = 0
            
        return {
            'part_type': 'screw',
            'diameter': head_width,
            'length': shaft_length
        }
        
        
        
        """print(f"螺丝头部宽度（估计）：{head_width:.2f} px")
        print(f"螺丝杆部长度（估计）：{shaft_length:.2f} px")
        """

"""
    if __name__ == '__main__':
    img_path = r'C:\pic\img1.jpg'
    img_processing(img_path)
    """