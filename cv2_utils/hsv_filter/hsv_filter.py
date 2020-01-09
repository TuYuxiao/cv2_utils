import cv2
import numpy as np
from ..utils import ConfigLoader, params_merger


class HSVFilter:
    WINDOW_NAME = 'hsv'

    def __init__(self, config_file_name='hsv', debug=False, **params):
        """

        :param config_file_name: The config file that would store the configured parameters automatically
        :param debug: show the cv slide bar to adjust parameter if True
        :param params: directly indicate parameters for Hough circle detection,
                        default params: {'low_H': 0, 'high_H': 255, 'low_S': 0, 'high_S': 255, 'low_V': 0, "high_V": 255}
        """
        self.config_loader = ConfigLoader(config_file_name)

        self.param = self.config_loader.load(
            default_param={'low_H': 0, 'high_H': 255, 'low_S': 0, 'high_S': 255, 'low_V': 0, "high_V": 255})
        for key, val in params.items():
            if self.param.get(key):
                self.param[key] = val

        if debug:
            cv2.namedWindow(self.WINDOW_NAME)
            for param, val in self.param.items():
                cv2.createTrackbar(param, self.WINDOW_NAME, val, 255, self.change(param))

    def filter(self, image, **params):
        frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        merged_params = params_merger(params, self.param)
        frame_threshold = cv2.inRange(frame_HSV, (merged_params('low_H'), merged_params('low_S'), merged_params('low_V')),
                                      (merged_params('high_H'), merged_params('high_S'), merged_params('high_V')))
        return frame_threshold

    def change(self, var):
        def feedback(x):
            self.param[var] = x
            print(var, self.param.get(var))
            self.save_param()

        return feedback

    def save_param(self):
        self.config_loader.save(self.param)
