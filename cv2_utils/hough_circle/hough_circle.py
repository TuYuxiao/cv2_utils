import cv2
import numpy as np
from ..utils import ConfigLoader, params_merger


class HoughCircleDetector:
    WINDOW_NAME = 'hough_circle'

    def __init__(self, config_file_name='hough_circle', debug=False, **params):
        """

        :param config_file_name: The config file that would store the configured parameters automatically
        :param debug: show the cv slide bar to adjust parameter if True
        :param params: directly indicate parameters for Hough circle detection,
                        default params: {'dist': 10, 'param1': 100, 'param2': 48, 'minRadius': 12, 'maxRadius': 25}
        """
        self.config_loader = ConfigLoader(config_file_name)

        self.param = self.config_loader.load(default_param={'dist': 10, 'param1': 100, 'param2': 48, 'minRadius': 12, 'maxRadius': 25})
        for key, val in params.items():
            if self.param.get(key):
                self.param[key] = val

        if debug:
            cv2.namedWindow(self.WINDOW_NAME)
            for param, val in self.param.items():
                cv2.createTrackbar(param, self.WINDOW_NAME, val, 255, self.change(param))

    def detect(self, img, **params):
        if len(img.shape) == 3 and img.shape[-1] == 3:  # color image
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        merged_params = params_merger(params, self.param)

        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1,
                                   merged_params('dist'), param1=merged_params('param1'),
                                   param2=merged_params('param2'), minRadius=merged_params('minRadius'),
                                   maxRadius=merged_params('maxRadius'))
        if circles is None:
            return []
        circles = np.uint16(np.around(circles))
        return circles[0].tolist()

    def render(self, target, circles, draw_center=True, draw_profile=True):
        for i in circles:
            if draw_profile:
                cv2.circle(target, (i[0], i[1]), i[2], (0, 255, 0), 2)
            if draw_center:
                cv2.circle(target, (i[0], i[1]), 2, (255, 0, 0), 3)

    def change(self, var):
        def feedback(x):
            self.param[var] = x
            print(var, self.param.get(var))
            self.save_param()

        return feedback

    def save_param(self):
        self.config_loader.save(self.param)
