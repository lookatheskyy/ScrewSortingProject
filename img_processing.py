import time
import cv2
import numpy as np

import os
import sensors


"""
————————————————————————————————————————————————————————————————————————————————————————————————————————


Image processing function:
After receiving a photo from the camera, perform image preprocessing and obtain the diameter and length (in pixels).

——————————————————————————————————————————————————————————————————————————————————————————————————————————

"""


def preprocess(img, save_steps=True, output_dir="debug_steps", base_name='1'):
    """
    Image Preprocessing
    Convert the original image into a clean binary image where contours can be easily extracted
    
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Grayscale conversion
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))  # Enhance contrast
    gray_clahe = clahe.apply(gray)  
    gray_blur = cv2.medianBlur(gray_clahe, 5) # Median filter
    if save_steps and output_dir:
        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_gray.png"), gray)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)   # Threshold Binarization (OSTU)
    if save_steps and output_dir:
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_thresh.png"), thresh)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=10)   # Morphological closing and opening operations for denoising
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)
    if save_steps and output_dir:
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_closed.png"), closed)
        cv2.imwrite(os.path.join(output_dir, f"{base_name}_opened.png"), opened)  
    return opened



"""
Object Detection & Measurement

"""

# Find all contours from the binary image and return the contour with the largest area as the contour of the target detection object
def largest_contour(mask):   
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    return max(contours, key=cv2.contourArea)

# Calculate the minimum enclosing rectangle of the target contour
def min_rect(contour, pixel_to_mm=1.0):
    
    rect = cv2.minAreaRect(contour)
    (cx, cy), (w, h), angle = rect

    
    if h > w:
        w, h = h, w
        angle += 90

    w_mm = w * pixel_to_mm
    h_mm = h * pixel_to_mm

   # Simple classification basis: Nuts with a width-to-height ratio close to 1 (0.8-1.2) are classified as nuts, otherwise they are screws
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

#Crop ROI and call the above two functions.
def img_recog(image_path, roi, pixel_to_mm=0.035, save_steps=True, output_dir="debug_steps"):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to read image at {image_path}")
   
   
    x, y, w, h = roi
    img_crop = img[y:y+h, x:x+w]
    
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    roi_tag = f"{base_name}_roi_{x}_{y}_{w}_{h}"
    

    
    if save_steps and output_dir:
        os.makedirs(output_dir, exist_ok=True)
        cv2.imwrite(os.path.join(output_dir, f"{roi_tag}_orig.png"), img_crop)

    
    mask = preprocess(img_crop, save_steps=save_steps, output_dir=output_dir, base_name=roi_tag)
   
    contour = largest_contour(mask)
    if contour is None:
        raise ValueError('No contour detected!')
    
    result = min_rect(contour, pixel_to_mm)

    
    if save_steps and output_dir:
        annotated = img_crop.copy()
     
        cv2.drawContours(annotated, [contour], -1, (0,0,255), 2)

        
        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(annotated, [box], 0, (0,255,0), 2)

      
        cx, cy = int(result['center'][0]), int(result['center'][1])
        cv2.circle(annotated, (cx, cy), 4, (255,0,0), -1)

       
        text = f"{result['part_type']} L_px:{int(result['length_px'])} D_px:{int(result['diameter_px'])}"
        cv2.putText(annotated, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        cv2.imwrite(os.path.join(output_dir, f"{roi_tag}_annotated.png"), annotated)
       
        cv2.imwrite(os.path.join(output_dir, f"{roi_tag}_mask.png"), mask)

    return result

