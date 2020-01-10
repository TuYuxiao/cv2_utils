import argparse
import cv2
from cv2_utils import RoiSelector, VideoCapture

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs='?', type=str, required=True,  help="Video input path")
    FLAGS = parser.parse_args()

    roi_selector = RoiSelector(500, 500, debug=True)

    cap = VideoCapture(FLAGS.input, show_video=False, loop=True)

    for img in cap:
        wrapped = roi_selector.wrap(img)
        cv2.imshow('wrapped', wrapped)
