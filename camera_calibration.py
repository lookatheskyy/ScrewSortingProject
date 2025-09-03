import cv2
import numpy as np
import glob



class CameraCalibration:
    def __init__(self, chessboard_size=(9,6), square_size=0.02):
        self.chessboard_size = chessboard_size
        self.square_size = square_size
        self.camera_matrix = None
        self.dist_coeffs = None

    def calibrate(self, images_path_pattern):
        objp = np.zeros((self.chessboard_size[0]*self.chessboard_size[1],3), np.float32)
        objp[:,:2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1,2)
        objp *= self.square_size

        objpoints = []
        imgpoints = []

        images = glob.glob(images_path_pattern)
        for fname in images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
            if ret:
                objpoints.append(objp)
                imgpoints.append(corners)

        if not objpoints:
            raise RuntimeError("No chessboard corners found. Check calibration images.")

        ret, camera_matrix, dist_coeffs, _, _ = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        if not ret:
            raise RuntimeError("Calibration failed.")

        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs

        # 保存文件
        np.savez('camera_calib.npz', camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)
        print("Calibration successful! Parameters saved to camera_calib.npz")

    def load_calibration(self, filepath='camera_calib.npz'):
        data = np.load(filepath)
        self.camera_matrix = data['camera_matrix']
        self.dist_coeffs = data['dist_coeffs']
        print(f"Loaded calibration from {filepath}")

    def undistort(self, img):
        if self.camera_matrix is None or self.dist_coeffs is None:
            raise RuntimeError("Calibration parameters not loaded")
        return cv2.undistort(img, self.camera_matrix, self.dist_coeffs)