import argparse
import cv2
from cv2_utils import HSVFilter, VideoCapture

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs='?', type=str, required=True,  help="Video input path")
    FLAGS = parser.parse_args()

    hsv_filter = HSVFilter(debug=True)

    cap = VideoCapture(FLAGS.input, show_video=False, max_fps=30, loop=True)

    for img in cap:
        thresh = hsv_filter.filter(img)
        cv2.imshow('hsv_filter_example', thresh)
