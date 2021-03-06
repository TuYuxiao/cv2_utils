import cv2
import numpy as np
from cv2_utils.utils import params_merger
from cv2_utils.layers import ParamLayer, Layer


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
        super().debug_setup()
        for param, val in self.param.items():
            cv2.createTrackbar(param, self.layer_name, val, 255, self.change(param))

    def inference(self, img, **params):
        return self.filter(img, **params)

    def filter(self, image, **params):
        frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        merged_params = params_merger(params, self.param)
        frame_threshold = cv2.inRange(frame_HSV, (merged_params('low_H'), merged_params('low_S'), merged_params('low_V')),
                                      (merged_params('high_H'), merged_params('high_S'), merged_params('high_V')))
        return frame_threshold

    def __add__(self, other):
        return CompositeHSVFilter(self, other)


class CompositeHSVFilter(Layer):
    def __init__(self, *layers):
        self.layers = layers
        assert len(layers) >= 2

    def inference(self, img, **params):
        dst = cv2.add(self.layers[0].inference(img), self.layers[1].inference(img))
        for i in range(2, len(self.layers)):
            dst = cv2.add(dst, self.layers[i].inference(img))
        return dst

    def __add__(self, other):
        return CompositeHSVFilter(*self.layers, other)
