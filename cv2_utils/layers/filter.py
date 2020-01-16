import cv2
from cv2_utils.layers import ParamLayer
from cv2_utils.utils import params_merger


class GaussianFilter(ParamLayer):
    DEFAULT_PARAM = {'ksize': 5, 'sigma': 0}

    def __init__(self, layer_name="default", debug=False, **params):
        super().__init__(layer_name, debug, **params)

    def filter(self, img, **params):
        merged_params = params_merger(params, self.param)
        ksize_max = min(img.shape[:2])//2
        ksize = min(merged_params('ksize'), ksize_max - (ksize_max + 1) % 2)
        return cv2.GaussianBlur(img, (ksize, ksize), merged_params('sigma'))

    def debug_setup(self):
        super().debug_setup()

        def feedback(x):
            var = 'ksize'
            self.param[var] = x - (x + 1) % 2 if x > 0 else 1
            print(var, self.param.get(var))
            self.save_param()

        cv2.createTrackbar('ksize', self.layer_name, self.param['ksize'], 255, feedback)
        cv2.createTrackbar('sigma', self.layer_name, self.param['sigma'], 255, self.change('sigma'))

    def inference(self, img):
        return self.filter(img)
