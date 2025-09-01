import cv2
import time
import os

def capture_image(camera_index=0, 
                  save_dir='captured_images', 
                  filename_prefix='capture',
                  width=1920, 
                  height=1080):
    """
    调用USB摄像头采集一张图片，设置分辨率并保存到文件夹
    
    :param camera_index: 摄像头索引号，默认0
    :param save_dir: 图片保存目录
    :param filename_prefix: 文件名前缀
    :param width: 期望图像宽度
    :param height: 期望图像高度
    :return: 保存的图片路径
    """

    # 创建文件夹
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    cap = cv2.VideoCapture(camera_index,cv2.CAP_V4L2)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # 采集几帧用于摄像头预热
    for _ in range(10):
        ret, frame = cap.read()
        if not ret:
            raise IOError("Failed to capture image from camera")
        # 可加小延时增强稳定
        time.sleep(0.05)

    # 取最后一帧
    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise IOError("Failed to capture final image")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.jpg"
    filepath = os.path.join(save_dir, filename)

    cv2.imwrite(filepath, frame)

    cap.release()
    return filepath
