import argparse
import cv2
from cv2_utils import HSVFilter, RoiSelector, GaussianFilter, VideoCapture, Sequential

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs='?', type=str, required=True,  help="Video input path")
    FLAGS = parser.parse_args()

    model = Sequential()
    model.add(VideoCapture(FLAGS.input, show_video=False, loop=True))
    model.add(RoiSelector(500, 500, debug=True))
    model.add(GaussianFilter(ksize=5, debug=True))
    model.add(HSVFilter(debug=True))

    for thresh in model:
        cv2.imshow('thresh', thresh)