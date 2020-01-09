import os
import json
import sys
import base64


class ConfigLoader:
    USER = 0
    LOCAL = 1
    PACKAGE = 2

    def __init__(self, name, mode=USER):
        if mode == self.USER:
            param_dir = os.path.expanduser('~/.cv2_utils/param')
        elif mode == self.LOCAL:
            param_dir = os.path.abspath('./param')
        elif mode == self.PACKAGE:
            param_dir = os.path.join(os.path.dirname(__file__), 'param')
        else:
            assert 1, "invalid mode"

        if not os.path.exists(param_dir):
            os.makedirs(param_dir)

        if name.startswith('/'):
            name = name[1:]
        else:
            exec_file = os.path.realpath(sys.argv[0])
            ns = base64.b16encode(exec_file.encode()).decode()[:10]
            name = os.path.join(ns,name)

        self.config_file_path = os.path.join(param_dir, name+".json")

        if not os.path.exists(os.path.dirname(self.config_file_path)):
            os.makedirs(os.path.dirname(self.config_file_path))

    def load(self, default_param):
        try:
            with open(self.config_file_path, 'r') as f:
                return json.load(f)
        except:
            return default_param

    def save(self, param):
        with open(self.config_file_path, 'w') as f:
            json.dump(param, f)
