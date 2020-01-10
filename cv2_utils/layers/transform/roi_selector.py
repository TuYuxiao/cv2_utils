import cv2
import numpy as np
from cv2_utils.layers import ParamLayer


class RoiSelector(ParamLayer):
    WINDOW_NAME = 'roi'

    def __init__(self, width, height, layer_name="default", debug=False, **params):
        """

        :param width: width of wrapped image
        :param height: height of wrapped image
        :param config_file_name: The config file that would store the configured parameters automatically
        :param debug: show the cv slide bar to adjust parameter if True
        :param params: directly indicate parameters for Hough circle detection,
                        default params: {'roi': [[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]]}
        """

        self.width = width
        self.height = height
        self.DEFAULT_PARAM = {'roi': [[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]]}

        super().__init__(layer_name, debug, **params)

        self.pts_d = np.float32(
            [[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]])

        self.roi = np.float32(self.param['roi'])
        self.n_point = 0
        self.M = cv2.getPerspectiveTransform(self.roi, self.pts_d)

    def debug_setup(self):
        cv2.namedWindow(self.layer_name)
        cv2.setMouseCallback(self.layer_name, self.mouse_click)

    def inference(self, img):
        return self.wrap(img)

    def mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.roi[self.n_point][0] = x
            self.roi[self.n_point][1] = y
            self.n_point += 1
            if self.n_point >= 4:
                self.n_point = 0
                self.M = cv2.getPerspectiveTransform(self.roi, self.pts_d)
                self.config_loader.save({'roi': self.roi.tolist()})

    def wrap(self, img, **params):
        if params.get('roi'):
            M = cv2.getPerspectiveTransform(params.get('roi'), self.pts_d)
        else:
            M = self.M

        if self.debug:
            image = img.copy()
            for i in [0,3]:
                for j in [1,2]:
                    cv2.line(image, (self.roi[i][0],self.roi[i][1]), (self.roi[j][0],self.roi[j][1]), (0,0,255), 2)

            cv2.imshow(self.layer_name, image)
            cv2.waitKey(1)

        return cv2.warpPerspective(img, M, (self.width, self.height))
