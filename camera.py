# camera.py

import cv2
import time
import os


"""
————————————————————————————————————————————————————————————————————————————————————————————————————————
实现的功能：
用树莓派控制usb camera（IMX179）获取图像，存储为图片。作为图像处理的输入。

-------------------------------------------
English：
Functionality implemented:
Use a Raspberry Pi to control a USB camera (IMX179) to capture images and store them as images. This serves as input for image processing.

——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""



# 定义了函数，用于控制usb摄像头调动拍照和保存。
def capture_image(camera_index=0,            # 摄像头索引号
                  save_dir='captured_images',    #图片保存路径
                  filename_prefix='capture',    # 文件名前缀，用于生成图片文件名
                  width=1280,    
                  height=720):
    """
    Call the USB camera to capture a picture, set the resolution and save it to a folder (调用USB摄像头采集一张图片，设置分辨率并保存到文件夹)
    
    :param camera_index: 摄像头索引号，默认0
    :param save_dir: 图片保存目录
    :param filename_prefix: 文件名前缀
    :param width: 期望图像宽度
    :param height: 期望图像高度
    :return: 保存的图片路径
    """

    # Create a folder 创建文件夹
    if not os.path.exists(save_dir):    # 检查save_dir目录是否存在，若不存在则创建它
        os.makedirs(save_dir)         # 创建多级目录

    # 创建一个摄像头采集对象cap
    cap = cv2.VideoCapture(camera_index,cv2.CAP_V4L2)   
    if not cap.isOpened():     # 判断摄像头上是否成功打开
        raise IOError("Cannot open webcam")


    # Set the resolution 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    # Capture a few frames for camera warm-up 采集几帧用于摄像头预热
    for _ in range(20):   # 连续采集20帧
        ret, frame = cap.read()
        if not ret:
            raise IOError("Failed to capture image from camera")
        # 可加小延时增强稳定
        time.sleep(0.05)  # 每采集一帧暂停0.05秒，有助于摄像头稳定

    # Take the last frame 取最后一帧
    ret, frame = cap.read()   # 再次调用cap.red获取一帧
    if not ret:
        cap.release()
        raise IOError("Failed to capture final image")
    
    
    
    


    timestamp = time.strftime("%Y%m%d_%H%M%S")    # 获取当前时间字符串，格式是年月日时分秒
    filename = f"{filename_prefix}_{timestamp}.jpg"
    filepath = os.path.join(save_dir, filename)

    cv2.imwrite(filepath, frame)

    cap.release()
    return filepath

