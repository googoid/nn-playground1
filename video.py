import numpy as np
import cv2
import time
import sys
import tensorflow as tf
from tensorflow.keras.applications.xception import Xception

model = Xception(include_top=False)

cap = cv2.VideoCapture('DJI_0037.MP4')
fps = cap.get(cv2.CAP_PROP_FPS)

paused = False

while cap.isOpened():
    if not paused:
        now = time.time()

        ret, frame = cap.read()

        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rescaled = cv2.resize(frame, (720, 480))

        timeDiff = time.time() - now
        if timeDiff < 1.0/(fps):
            time.sleep(1.0/(fps) - timeDiff)

        processed = tf.keras.applications.xception.preprocess_input(rescaled)

        pred = model.predict(np.array([processed]))
        print(pred.shape)
        print('0:', pred[0].shape)
        print('0,0:', pred[0][0].shape)
        print('0,1:', pred[0][1].shape)
        print('0,2:', pred[0][2].shape)

        # stack = np.hstack((rescaled, None))
        stack = np.hstack(pred[0, :, :, 0:10])
        cv2.imshow('frame', rescaled)
        cv2.imshow('filter', stack)

    key = cv2.waitKey(1)

    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord(' '):
        paused = not paused

cap.release()
cv2.destroyAllWindows()
