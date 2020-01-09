import cv2
import numpy as np
from ..utils import ConfigLoader

class RoiSelector:
    WINDOW_NAME = 'roi'

    def __init__(self, width, height, config_file_name='roi', debug=False):
        self.width = width
        self.height = height
        self.debug = debug
        self.config_loader = ConfigLoader(config_file_name)

        self.pts_d = np.float32(
            [[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])

        param = self.config_loader.load(
            default_param={'roi': [[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]]})

        self.roi = np.float32(param['roi'])
        self.n_point = 0
        self.M = cv2.getPerspectiveTransform(self.roi, self.pts_d)

        if debug:
            cv2.namedWindow(self.WINDOW_NAME)
            cv2.setMouseCallback(self.WINDOW_NAME, self.mouse_click)

    def mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.roi[self.n_point][0] = x
            self.roi[self.n_point][1] = y
            self.n_point += 1
            if self.n_point >= 4:
                self.n_point = 0
                self.M = cv2.getPerspectiveTransform(self.roi, self.pts_d)
                self.config_loader.save({'roi': self.roi.tolist()})

    def wrap(self, img):
        if self.debug:
            image = img.copy()
            for i in [0,3]:
                for j in [1,2]:
                    cv2.line(image, (self.roi[i][0],self.roi[i][1]), (self.roi[j][0],self.roi[j][1]), (0,0,255), 2)

            cv2.imshow(self.WINDOW_NAME, image)
            cv2.waitKey(1)

        return cv2.warpPerspective(img, self.M, (self.width, self.height))
