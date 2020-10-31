import numpy as np
import cv2
import time
import sys
import os

cap = cv2.VideoCapture('DJI_0037.MP4')
fps = 240  # cap.get(cv2.CAP_PROP_FPS)

train_annots_dir = 'dataset/train/annots'
train_images_dir = 'dataset/train/images'
labels = ['car', 'truck', 'bus', 'tank']
label_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
                (255, 255, 0), (255, 0, 255)]

selectedLabelIdx = 0

paused = False
prevFrame = None

roiSize = 100

frame = None
overlayFrame = np.zeros((10, 10))

idx = 0
for _, _, files in os.walk('data/train/car'):
    for name in files:
        seq = int(name.split('.')[0])
        idx = max((idx, seq))
idx += 1

isDragging = False

bboxes = []


def save_frame_and_bboxes(index, frame, bboxes):
    filename = str(index).zfill(10) + '.jpg'
    image_path = train_images_dir + '/' + filename
    annots_path = train_annots_dir + '/' + str(index).zfill(10) + '.xml'

    objects = []

    for bbox in bboxes:
        objects.append("""<object>
        <name>%s</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>%d</xmin>
            <ymin>%d</ymin>
            <xmax>%d</xmax>
            <ymax>%d</ymax>
        </bndbox>
    </object>""" % (labels[bbox[0]], bbox[1], bbox[2], bbox[3], bbox[4]))

    xml = """<annotation verified="yes">
    <folder>Annotation</folder>
    <filename>%s</filename>
    <path>%s</path>
    <source>
        <database>Unknown</database>
    </source>
    <size>
        <width>%d</width>
        <height>%d</height>
        <depth>%d</depth>
    </size>
    <segmented>0</segmented>
    %s
</annotation>""" % (filename, image_path, frame.shape[1], frame.shape[0], frame.shape[2], '\n    '.join(objects))

    cv2.imwrite(image_path, frame)
    with open(annots_path, 'w+') as f:
        f.write(xml)


def mouse_callback(event, x, y, flags, param):
    global roiX1, roiY1, roiX2, roiY2, overlayFrame, paused, idx, isDragging, bboxes, selectedLabelIdx

    if not paused:
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        isDragging = True
        bboxes.append([selectedLabelIdx, x, y, 0, 0])
    elif event == cv2.EVENT_LBUTTONUP:
        # swap points if needed, first one should always be the minimum point
        x1, y1, x2, y2 = bboxes[len(bboxes) - 1][1:5]
        bboxes[len(bboxes) - 1] = [bboxes[len(bboxes) - 1][0],
                                   min([x1, x2]), min([y1, y2]), max([x1, x2]), max([y1, y2])]

        print(bboxes[len(bboxes) - 1])

        isDragging = False
    elif event == cv2.EVENT_MOUSEMOVE:
        if not isDragging:
            return
        bboxes[len(bboxes) - 1][3] = x
        bboxes[len(bboxes) - 1][4] = y


cv2.namedWindow('frame')
cv2.setMouseCallback('frame', mouse_callback)

while cap.isOpened():
    if not paused:
        now = time.time()

        ret, frame = cap.read()
        prevFrame = frame

        timeDiff = time.time() - now
        if timeDiff < 1.0/(fps):
            time.sleep(1.0/(fps) - timeDiff)

    idx += 1
    overlayFrame = np.copy(prevFrame)

    if len(bboxes) > 0:
        for bbox in bboxes:
            if not bbox[2] or not bbox[3]:
                continue
            cv2.rectangle(
                overlayFrame, (bbox[1], bbox[2]), (bbox[3], bbox[4]), label_colors[bbox[0]])

    cv2.imshow('frame', overlayFrame)

    key = cv2.waitKey(1)

    if key & 0xFF == ord('q'):
        break

    if key & 0xFF == ord(' '):
        overlayFrame = np.copy(frame)
        if paused:
            bboxes = []
        paused = not paused

    if key & 0xFF == ord('x') and len(bboxes) > 0:
        bboxes = bboxes[:len(bboxes) - 1]

    for i in range(1, 9):
        if key & 0xFF == ord(str(i)):
            labelIdx = (key & 0xFF) - ord('1')
            if labelIdx > len(labels) - 1:
                continue
            selectedLabelIdx = labelIdx
            print('Selected Label:', labels[selectedLabelIdx])

    if key & 0xFF == 13:
        if paused:
            paused = not paused

            save_frame_and_bboxes(idx, prevFrame, bboxes)

            bboxes = []


cap.release()
cv2.destroyAllWindows()
