import os
import sys
import base64
from cv2_utils.utils import ConfigLoader


class Layer:
    def __init__(self, layer_name='default'):

        # TODO automatically generate layer name
        if layer_name.startswith('/'):  # abs
            layer_name = "%s_%s" % (self.__class__.__name__, layer_name[1:])
        else:  # relative
            exec_file = os.path.realpath(sys.argv[0])
            ns = base64.b16encode(exec_file.encode()).decode()[:10]
            layer_name = os.path.join(ns, "%s_%s" % (self.__class__.__name__, layer_name))

        self.layer_name = layer_name

    def inference(self, img):
        return img


class ParamLayer(Layer):
    DEFAULT_PARAM = {}

    def __init__(self, layer_name='default', debug=False, **params):
        super().__init__(layer_name=layer_name)

        self.config_loader = ConfigLoader(self.layer_name)

        self.param = self.config_loader.load(default_param=self.DEFAULT_PARAM)
        for key, val in params.items():
            if self.param.get(key):
                self.param[key] = val

        self.debug = debug
        if self.debug:
            self.debug_setup()

    def debug_setup(self):
        pass

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
        assert False, "Source layer should called"
