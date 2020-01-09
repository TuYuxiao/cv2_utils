from abc import abstractmethod

import cv2
import sys

version_info = sys.version_info


class VideoCapture:
    def __init__(self, file_path, loop=True):
        self.gen = Generator.get_generator(file_path, loop)

    def read(self, gray = False):
        ret, img = self.gen.read()
        if gray and ret:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return ret, img


class Generator:
    GENERATORS = []

    def __init__(self, file_path, loop):
        self.file_path = file_path
        self.loop = loop

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.GENERATORS.append(cls)

    def set_loop(self):
        self.loop = True

    def unset_loop(self):
        self.loop = False

    @abstractmethod
    def read(self):
        return False, None

    @classmethod
    def check(cls, file_path):
        return False

    @classmethod
    def get_generator(cls, file_path, loop):
        if version_info.major == 3 and version_info.minor >= 6:
            gens = cls.GENERATORS
        else:
            gens = [ImageGenerator, VideoGenerator, CameraGenerator, RosVideoGenerator]

        for gen in gens:
            if gen.check(file_path):
                return gen(file_path, loop)
        assert False, "no valid generator"


class ImageGenerator(Generator):
    def __init__(self, file_path, loop):
        if version_info.major == 3:
            super().__init__(file_path, loop)
        else:
            Generator.__init__(self, file_path, loop)
        self.image = cv2.imread(file_path)
        assert self.image is not None

        self.first_read = True

    def read(self):
        if not self.first_read:
            self.first_read = False
        if self.loop or self.first_read:
            return True, self.image
        return False, None

    @classmethod
    def check(cls, file_path):
        file_path = file_path.lower()
        if file_path.endswith('.jpg') or file_path.endswith('.jpeg') \
                or file_path.endswith('.png') or file_path.endswith('.tiff') \
                or file_path.endswith('.bmp'):
            return True
        return False


class VideoGenerator(Generator):
    def __init__(self, file_path, loop):
        if version_info.major == 3:
            super().__init__(file_path, loop)
        else:
            Generator.__init__(self, file_path, loop)
        self.cap = cv2.VideoCapture(file_path)
        assert self.cap.read()[0]
        self.reset()

    def reset(self):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def read(self):
        ret, frame = self.cap.read()
        if (not ret) and self.loop:
            self.reset()
            ret, frame = self.cap.read()
        return ret, frame

    @classmethod
    def check(cls, file_path):
        file_path = file_path.lower()
        if file_path.endswith('.mp4') or file_path.endswith('.avi'):
            return True
        return False


class CameraGenerator(Generator):
    def __init__(self, file_path, loop):
        if version_info.major == 3:
            super().__init__(file_path, loop)
        else:
            Generator.__init__(self, file_path, loop)
        self.cap = cv2.VideoCapture(file_path)

    def read(self):
        return self.cap.read()

    @classmethod
    def check(cls, file_path):
        if isinstance(file_path, int):
            return True
        if file_path.startswith('http://') or file_path.startswith('https://'):
            return True
        return False


class RosVideoGenerator(Generator):
    def __init__(self, file_path, loop):
        if version_info.major == 3:
            super().__init__(file_path, loop)
        else:
            Generator.__init__(self, file_path, loop)
        import rospy
        from cv_bridge import CvBridge, CvBridgeError
        from sensor_msgs.msg import Image
        from queue import Queue
        rospy.init_node('ros_video_capture', anonymous=True)
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber(file_path, Image, self.callback)
        self.image_queue = Queue(maxsize=3)

    def callback(self, data):
        try:
            image = self.bridge.imgmsg_to_cv2(data, "bgr8")
            if self.image_queue.full():
                self.image_queue.get_nowait()
            self.image_queue.put_nowait(image)
        except Exception as e:
            print(e)

    def read(self):
        return True, self.image_queue.get()

    @classmethod
    def check(cls, file_path):
        if version_info.major == 3:  # cv_bridge is not support python3 currently TODO
            return False
        import rospy
        if file_path in [topic[0] for topic in rospy.get_published_topics()]:
            return True
        print([topic[0] for topic in rospy.get_published_topics()])
        return False
