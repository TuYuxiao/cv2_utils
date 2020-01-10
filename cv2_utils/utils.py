import os
import json
import copy


def params_merger(params_prioritized, params):
    def merger(key):
        return params_prioritized.get(key) if params_prioritized.get(key) else params[key]
    return merger


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

        self.config_file_path = os.path.join(param_dir, name + ".json")

        if not os.path.exists(os.path.dirname(self.config_file_path)):
            os.makedirs(os.path.dirname(self.config_file_path))

    def load(self, default_param):
        param = copy.deepcopy(default_param)
        try:

            with open(self.config_file_path, 'r') as f:
                stored_param = json.load(f)
                if isinstance(stored_param, dict):
                    param.update(stored_param)
        except:
            pass

        return param

    def save(self, param):
        with open(self.config_file_path, 'w') as f:
            json.dump(param, f)
