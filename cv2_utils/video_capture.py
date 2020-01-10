from abc import abstractmethod

import cv2
import sys
import time
from collections import deque

from cv2_utils.layers import SourceLayer

version_info = sys.version_info


class VideoCapture(SourceLayer):
    def __init__(self, file_path, layer_name="default", exit_keys=[27, ord('q')], max_fps=0, show_video=False, show_fps=False, loop=False):
        super().__init__(layer_name=layer_name)

        self.gen = Generator.get_generator(file_path, loop)
        self.exit_keys = exit_keys
        self.show_video = show_video
        self.show_fps = show_fps
        self.max_fps = max_fps
        self.last_pressed_key = -1

        self.last_frame = None

        self.previous_frames_time = deque(maxlen=5)

    def read(self, gray=False):
        ret, img = self.gen.read()
        if gray and ret:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return ret, img

    def show_frame(self, frame):
        if self.last_frame is not None:

            # add fps display
            if self.show_fps and len(self.previous_frames_time) == self.previous_frames_time.maxlen:
                fps = (self.previous_frames_time.maxlen-1) / (self.previous_frames_time[-1] - self.previous_frames_time[0])
                cv2.putText(self.last_frame, 'FPS: %d' % round(fps), (5, 25), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

            cv2.imshow(self.layer_name, self.last_frame)
        self.last_frame = frame

    def __iter__(self):
        # TODO low fps for stream device such as video would cause buffer emit and result in high time delay
        # use a Thread/Process to continually clear the buffer and reduce the time delay
        return self

    def __next__(self):
        ret, frame = self.read()

        self.last_pressed_key = cv2.waitKey(1)
        if (not ret) or self.last_pressed_key in self.exit_keys:
            raise StopIteration

        if self.show_video:
            self.show_frame(frame)

        # fps limit
        current_time = time.time_ns()/1e9
        if len(self.previous_frames_time) > 0 and self.max_fps > 0:
            dt = current_time - self.previous_frames_time[-1]
            sleep_time = 1./self.max_fps - dt
            if sleep_time > 0:
                time.sleep(sleep_time)
        self.previous_frames_time.append(time.time_ns()/1e9)

        return frame

    def get_last_pressed_key(self):
        return self.last_pressed_key


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
        if self.loop or self.first_read:
            self.first_read = False
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

        return False
