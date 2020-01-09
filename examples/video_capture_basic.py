import argparse
from cv2_utils import VideoCapture

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", nargs='?', type=str, required=True,  help="Video input path")
    FLAGS = parser.parse_args()

    cap = VideoCapture(FLAGS.input, show_video=True, show_fps=True, max_fps=0)

    for img in cap:
        pass
