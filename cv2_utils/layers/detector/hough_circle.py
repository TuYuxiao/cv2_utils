import cv2
import numpy as np
from cv2_utils.utils import params_merger
from cv2_utils.layers import ParamLayer


class HoughCircleDetector(ParamLayer):
    DEFAULT_PARAM = {'dist': 10, 'param1': 100, 'param2': 48, 'minRadius': 12, 'maxRadius': 25}

    def __init__(self, layer_name="default", debug=False, **params):
        """

        :param config_file_name: The config file that would store the configured parameters automatically
        :param debug: show the cv slide bar to adjust parameter if True
        :param params: directly indicate parameters for Hough circle detection,
                        default params: {'dist': 10, 'param1': 100, 'param2': 48, 'minRadius': 12, 'maxRadius': 25}
        """
        super().__init__(layer_name, debug, **params)

    def debug_setup(self):
        cv2.namedWindow(self.layer_name)
        for param, val in self.param.items():
            cv2.createTrackbar(param, self.layer_name, val, 255, self.change(param))

    def inference(self, img):
        return self.detect(img)

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
