import cv2
import numpy as np
from ..utils import ConfigLoader


class HSVFilter:
    WINDOW_NAME = 'hsv'

    def __init__(self, config_file_name='hsv', debug=False):
        self.config_loader = ConfigLoader(config_file_name)

        self.param = self.config_loader.load(
            default_param={'low_H': 0, 'high_H': 255, 'low_S': 0, 'high_S': 255, 'low_V': 0, "high_V": 255})

        if debug:
            cv2.namedWindow(self.WINDOW_NAME)
            for param, val in self.param.items():
                cv2.createTrackbar(param, self.WINDOW_NAME, val, 255, self.change(param))

    def filter(self, image):
        frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        frame_threshold = cv2.inRange(frame_HSV, (self.param['low_H'], self.param['low_S'], self.param['low_V']),
                                      (self.param['high_H'], self.param['high_S'], self.param['high_V']))
        return frame_threshold

    def change(self, var):
        def feedback(x):
            self.param[var] = x
            print(var, self.param.get(var))
            self.save_param()

        return feedback

    def save_param(self):
        self.config_loader.save(self.param)
