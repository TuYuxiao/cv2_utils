import cv2
import numpy as np
from cv2_utils.layers import ParamLayer


class PolygonMask(ParamLayer):
    WINDOW_NAME = 'poly mask'

    def __init__(self, auto_clip=False, layer_name="default", debug=False, **params):
        """

        :param debug: show the cv slide bar to adjust parameter if True
        :param params: directly indicate parameters for Hough circle detection,
                        default params: {'roi': [[0, 0], [self.width, 0], [0, self.height], [self.width, self.height]]}
        """

        self.DEFAULT_PARAM = {'contour': []}

        super().__init__(layer_name, debug, **params)

        self.auto_clip = auto_clip
        self.contour = self.param['contour']
        self.mask = None
        self.contour_changed = False
        self.last_img_shape = [0, 0]

    def debug_setup(self):
        super().debug_setup()
        cv2.setMouseCallback(self.layer_name, self.mouse_click)

    def inference(self, img, **params):
        return self.masking(img, **params)

    def update_mask(self, img_shape):
        if len(self.contour) < 3:
            return None
        mask = np.zeros((img_shape[1],img_shape[0]), dtype='uint8')
        cv2.drawContours(mask, [np.array(self.contour)], -1, (255), -1)
        return mask

    def mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.contour.append(((x,y),))
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.contour.clear()

        self.contour_changed = True
        self.config_loader.save({'contour': self.contour})

    def masking(self, img, **params):
        if params.get('contour'):
            contour = params.get('contour')
        else:
            contour = self.contour

        if self.debug and (params.get('show') is None or params.get('show')):
            image = img.copy()
            for i in range(len(contour)):
                cv2.line(image, (contour[i][0][0], contour[i][0][1]), (contour[(i+1)%len(contour)][0][0], contour[(i+1)%len(contour)][0][1]), (0,0,255), 2)

            cv2.imshow(self.layer_name, image)
            cv2.waitKey(1)

        if self.last_img_shape[0] != img.shape[1] or self.last_img_shape[1] != img.shape[0] or self.contour_changed:
            img_shape = [img.shape[1], img.shape[0]]
            self.mask = self.update_mask(img_shape)
            self.last_img_shape = img_shape
            self.contour_changed = False

        if self.mask is None:
            return img

        masked_img = cv2.bitwise_and(img, img, mask=self.mask)
        if self.auto_clip and (not self.debug):
            rect = cv2.boundingRect(np.array(self.contour))
            masked_img = masked_img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2], :]
        return masked_img
