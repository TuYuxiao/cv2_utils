import os
import sys
import hashlib
import cv2
from cv2_utils.utils import ConfigLoader


class Layer:
    def __init__(self, layer_name='default'):

        # TODO automatically generate layer name

        exec_file = os.path.realpath(sys.argv[0])
        ns = hashlib.md5(exec_file.encode()).hexdigest()
        if layer_name.startswith('/'):  # abs
            layer_id = "%s_%s" % (layer_name[1:], self.__class__.__name__)
        else:  # relative
            layer_id = os.path.join("%s_%s" % (os.path.basename(exec_file), ns), "%s_%s" % (layer_name, self.__class__.__name__))

        self.layer_name = "%s_%s" % (layer_name, ns)
        self.layer_id = layer_id

    def inference(self, img, **params):
        return img

    def __call__(self, *args, **kwargs):
        assert len(args) == 1
        return self.inference(args[0], **kwargs)


class ParamLayer(Layer):
    DEFAULT_PARAM = {}

    def __init__(self, layer_name='default', debug=False, **params):
        super().__init__(layer_name=layer_name)

        self.config_loader = ConfigLoader(self.layer_id)

        self.param = self.config_loader.load(default_param=self.DEFAULT_PARAM)
        for key, val in params.items():
            if self.param.get(key):
                self.param[key] = val

        self.debug = debug
        if self.debug:
            self.debug_setup()

    def debug_setup(self):
        cv2.namedWindow(self.layer_name)

    def change(self, var):
        def feedback(x):
            self.param[var] = x
            print(var, self.param.get(var))
            self.save_param()

        return feedback

    def save_param(self):
        self.config_loader.save(self.param)


class SourceLayer(Layer):
    def __init__(self, layer_name='default'):
        super().__init__(layer_name=layer_name)

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def inference(self, img):
        assert False, "Source layer should not be called"
