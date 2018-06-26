import os
from PIL import Image
from xml.etree import ElementTree

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

classes = ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

def find_x_y_w_h(size, box):
    print(size[0])
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

os.chdir(r"D:/yolo_train/data/Annotations/")
files = os.listdir(r"D:/yolo_train/data/Annotations/")

for fout in files:
    foutName = "D:/yolo_train/data/Annotations/" + fout
    print(foutName)
    fin = open("D:/yolo_train/data/train/" + fout[:-4] + ".txt", "w+")

    with open(foutName , 'r') as f:
        tree = ET.parse(f)
        root = tree.getroot()

    for size in root.findall('size'):
        width = size.find('width').text
        height = size.find('height').text
        size =(float(width),float(height))
        print(size)

    for object in root.findall('object'):
        name = object.find('name').text
        print(name)

        bndbox = object.find('bndbox')
        xmin = bndbox.find('xmin').text
        xmax = bndbox.find('xmax').text
        ymin = bndbox.find('ymin').text
        ymax = bndbox.find('ymax').text
        box = (float(xmin),float(xmax),float(ymin),float(ymax))
        four_out = find_x_y_w_h(size,box)

        print xmin, xmax, ymin, ymax
        for i in range(len(classes)):
            if name == classes[i]:
                print(classes[i])
                print(i)
                fin.writelines("%d %f %f %f %f" % (i,four_out[0],four_out[1], four_out[2], four_out[3]))
                fin.writelines("\n")
    fin.close()
