import cv2
import time
import numpy as np
import copy

class CameraControl:
    """
    Class for establishing connection with camera
    """
    def __init__(self, camera_id = 0, resolution = (1920, 1080)):
        self.cap = cv2.VideoCapture(camera_id)
        self.set_resolution(resolution)
    
    def set_resolution(self, resolution):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    def take_pic(self, img_path, layerID):
        # img = self.get_pic()
        img = self.take_stable_pic()
        cv2.imwrite(img_path,img) #route
        print("success to save layer_{}.jpg".format(layerID))

    def get_pic(self):
        while(not self.cap.isOpened()): # check camera status
            pass

        ret_flag, img = self.cap.read() # get img
        return img
    
    def take_stable_pic(self, delay_time = 0.5, diff_threshold = 1.):
        diff_mean = 100
        img1 = self.get_pic()
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

        while diff_mean > diff_threshold or diff_mean == 0:
            time.sleep(delay_time)
            img2 = self.get_pic()
            img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            img_diff = cv2.subtract(img1_gray, img2_gray)
            diff_mean = np.mean(img_diff)
            print("img_diff: ", diff_mean)
            img1_gray = copy.copy(img2_gray)

        return img1

    def turn_off_cam(self):
        self.cap.release()
