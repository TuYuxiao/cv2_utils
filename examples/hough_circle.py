import argparse
from cv2_utils import HoughCircleDetector, VideoCapture

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs='?', type=str, required=True,  help="Video input path")
    FLAGS = parser.parse_args()

    circle_detector = HoughCircleDetector(debug=True, dist=10)  # directly indicate some parameters

    cap = VideoCapture(FLAGS.input, show_video=True, show_fps=True, loop=True)

    for img in cap:
        circles = circle_detector.detect(img, param1=100)
        circle_detector.render(img, circles)
