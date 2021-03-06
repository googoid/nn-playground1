import numpy as np
import cv2
import time
import sys
import tensorflow as tf
from tensorflow.keras.applications.vgg19 import VGG19
import os

model = VGG19(include_top=False)

cap = cv2.VideoCapture('DJI_0037.MP4')
fps = cap.get(cv2.CAP_PROP_FPS)

paused = False
prevFrame = None

roiSize = 100
roiX = None
roiY = None

frame = None
overlayFrame = None

idx = 0
for _, _, files in os.walk('data/train/car'):
    for name in files:
        seq = int(name.split('.')[0])
        idx = max((idx, seq))
idx += 1


def mouse_callback(event, x, y, flags, param):
    global roiX, roiY, overlayFrame, paused, idx

    if not paused:
        return

    if event == cv2.EVENT_MOUSEMOVE:
        roiX, roiY = x - int(roiSize / 2), y - int(roiSize / 2)
        if roiX < 0:
            roiX = 0
        if roiY < 0:
            roiY = 0
        if roiX + roiSize > overlayFrame.shape[1]:
            roiX = overlayFrame.shape[1] - roiSize
        if roiY + roiSize > overlayFrame.shape[0]:
            roiY = overlayFrame.shape[0] - roiSize
    elif event == cv2.EVENT_LBUTTONDOWN:
        cropped = prevFrame[roiY: roiY +
                            roiSize, roiX: roiX + roiSize]
        cv2.imwrite('data/train/car/' + str(idx).zfill(5) + '.jpg', cropped)
        idx += 1
        paused = False
        roiX = roiY = None


cv2.namedWindow('frame')
cv2.setMouseCallback('frame', mouse_callback)

while cap.isOpened():
    if not paused:
        now = time.time()

        ret, frame = cap.read()

        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rescaled = cv2.resize(frame, (720, 480))

        timeDiff = time.time() - now
        if timeDiff < 1.0/(fps):
            time.sleep(1.0/(fps) - timeDiff)

        # processed = tf.keras.applications.xception.preprocess_input(rescaled)

        # pred = model.predict(np.array([processed]))

        # stack = np.hstack((rescaled, None))
        # stack = np.hstack(
        #     (pred[0, :, :, 0], pred[0, :, :, 1], pred[0, :, :, 2], pred[0, :, :, 3]))
        prevFrame = rescaled
        # cv2.imshow('filter', stack)

    overlayFrame = np.copy(rescaled)

    if roiX != None and roiY != None:
        cv2.rectangle(overlayFrame, (roiX, roiY), (roiX + roiSize,
                                                   roiY + roiSize), color=(255, 0, 0), thickness=2)
    cv2.imshow('frame', overlayFrame)

    key = cv2.waitKey(1)

    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord(' '):
        paused = not paused
        # roi = cv2.selectROI('frame', prevFrame,
        #                     showCrosshair=False, fromCenter=False)
        # if np.sum(roi) != 0:
        #     print(roi)
        #     cropped = prevFrame[roi[1]: roi[1] +
        #                         roi[3], roi[0]: roi[0] + roi[2]]
        #     print(cropped.shape)
        #     cv2.imwrite("test.jpg", cropped)

    if paused:
        if key & 0xFF == ord('a'):
            roiSize += 10
            roiX -= 5
            roiY -= 5

        if key & 0xFF == ord('z'):
            roiSize -= 10
            roiX += 5
            roiY += 5

cap.release()
cv2.destroyAllWindows()
