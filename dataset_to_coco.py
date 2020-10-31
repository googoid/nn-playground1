import os
import xml.etree.ElementTree as ET

labels = {'car': 0}

for _, _, files in os.walk('dataset/train/annots'):
    for file in files:
        tree = ET.parse('dataset/train/annots/' + file)
        root = tree.getroot()

        # from xml
        filename = None
        width = None
        height = None
        objects = []

        for el in root.getchildren():
            if el.tag == 'size':
                for child in el.getchildren():
                    if child.tag == 'width':
                        width = int(child.text)
                    elif child.tag == 'height':
                        height = int(child.text)

            elif el.tag == 'filename':
                filename = el.text

        for el in root.getchildren():
            if el.tag == 'object':
                label = None
                xmin, ymin, xmax, ymax = None, None, None, None

                for obj in el.getchildren():
                    if obj.tag == 'name':
                        label = labels[obj.text]
                    elif obj.tag == 'bndbox':
                        for dim in obj.getchildren():
                            if dim.tag == 'xmin':
                                xmin = int(dim.text)
                            elif dim.tag == 'ymin':
                                ymin = int(dim.text)
                            elif dim.tag == 'xmax':
                                xmax = int(dim.text)
                            elif dim.tag == 'ymax':
                                ymax = int(dim.text)

                bwidth = xmax - xmin
                bheight = ymax - ymin

                objects.append([str(label), str((xmin + bwidth / 2) / width), str((ymin +
                                                                                   bheight / 2) / height), str(bwidth / width), str(bheight / height)])

        with open('coco/labels/train2017/' + filename.split('.')[0] + '.txt', 'w+') as f:
            f.write('\n'.join([' '.join(x) for x in objects]))

        with open('dataset/train/images/' + filename, 'rb') as src:
            with open('coco/images/train2017/' + filename, 'wb+') as dst:
                dst.write(src.read())
