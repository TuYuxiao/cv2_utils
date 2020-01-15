# cv2_utils

## Installation

`pip install cv2_utils`

## Usage

#### VideoCapture

VideoCapture wrapped OpenCV VideoCapture. It could open USB camera, 
video file, video stream and ROS topic.

VideoCapture could be used in the same way as OpenCV VideoCapture.

```
from cv2_utils import VideoCapture
cap = VideoCapture("example.avi")
while True:
    ret, img = cap.read()
    if not ret:
        break
    key = cv2.waitKey(1)
    if key == ord('q') or key == 27:
        break
    cv2.imshow('img', img)
```

Iterator is supported to fetch images from VideoCapture in a simpler way. 
VideoCapture would automatically show the original stream, limit the
fps and trigger the exit condition in this way.

```
from cv2_utils import VideoCapture
cap = VideoCapture("example.avi", show_video=True, show_fps=True)
for img in cap:
    pass
```

#### Layers
All image operations could be a layer in a CV task.
For many operators, there are many parameters needs to be configured.
However, it's not convenient to set and fine tune these parameters.

The parameters of layers such as HoughCircle, HSV thresholding  could be 
easily tuned with GUI (currently use based on OpenCV slide bar and mouse/keyboard callback, limited).
The parameters are automatically stored in configure files (under $HOME/.cv2_utils by default).
The name of layer needs to be indicated for better managing the configure parameters.

```
from cv2_utils import HoughCircleDetector, VideoCapture
circle_detector = HoughCircleDetector(debug=True)
cap = VideoCapture("example.avi",show_video=True, show_fps=True, loop=True)

for img in cap:
    circles = circle_detector.detect(img)
    circle_detector.render(img, circles)
``` 

#### Sequential
A sequential model is implemented to easier configure a CV pipeline.
A sequential with source (such as VideoCapture) could be used as a iterator.

```
from cv2_utils import HSVFilter, GaussianFilter, VideoCapture, Sequential

model = Sequential()
model.add(VideoCapture("example.avi", show_video=False, loop=True))
model.add(GaussianFilter(ksize=5, debug=True))
model.add(HSVFilter(debug=True))

for thresh in model:
    cv2.imshow('thresh', thresh)
```