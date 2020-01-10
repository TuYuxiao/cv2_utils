import cv2
import numpy as np
from cv2_utils.utils import params_merger
from cv2_utils.layers import ParamLayer


class HSVFilter(ParamLayer):
    WINDOW_NAME = 'hsv'
    DEFAULT_PARAM = {'low_H': 0, 'high_H': 255, 'low_S': 0, 'high_S': 255, 'low_V': 0, "high_V": 255}

    def __init__(self, layer_name="default", debug=False, **params):
        """

        :param config_file_name: The config file that would store the configured parameters automatically
        :param debug: show the cv slide bar to adjust parameter if True
        :param params: directly indicate parameters for Hough circle detection,
                        default params: {'low_H': 0, 'high_H': 255, 'low_S': 0, 'high_S': 255, 'low_V': 0, "high_V": 255}
        """
        super().__init__(layer_name, debug, **params)

    def debug_setup(self):
        cv2.namedWindow(self.layer_name)
        for param, val in self.param.items():
            cv2.createTrackbar(param, self.layer_name, val, 255, self.change(param))

    def inference(self, img):
        return self.filter(img)

    def filter(self, image, **params):
        frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        merged_params = params_merger(params, self.param)
        frame_threshold = cv2.inRange(frame_HSV, (merged_params('low_H'), merged_params('low_S'), merged_params('low_V')),
                                      (merged_params('high_H'), merged_params('high_S'), merged_params('high_V')))
        return frame_threshold
