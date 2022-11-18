import os 
import sys

import cv2

import numpy as np 

from PyQt5.QtGui import QImage
from PyQt5.QtCore import QPoint


def imread(imgPath):
    img = cv2.imdecode(np.fromfile(imgPath, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

    if img.ndim == 3 : 
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
    return img


def imwrite(path, img): 
    _, ext = os.path.splitext(path)
    _, label_to_file = cv2.imencode(ext, img)
    label_to_file.tofile(path)
    

def createLayersFromLabel(label, num_class):

    layers = []

    for idx in range(num_class):
        layers.append(label == idx)
        
    return layers


def getScaledPoint(event, scale):
    """Get scaled point coordinate 
    Args: 
        event (PyQt5 event)
        scale (float)

    Returns:
        x, y (PyQt5 Qpoint)
    """

    scaled_event_pos = QPoint(round(event.pos().x() / scale), round(event.pos().y() / scale))
    x, y = scaled_event_pos.x(), scaled_event_pos.y()

    return x, y 

def append_Path(file, level=1):
    """Append environmental path 

    Args: 
        file (str): file directory, mostly obtained by '__file__' variable. 
        level (int): number of parental folder to be added, default = 1 
    
    """

    for _ in range(level):
        append_to = os.path.dirname(os.path.abspath( os.path.dirname(file)))
        sys.path.append(append_to)


def cvtArrayToQImage(array):

    if len(array.shape) == 3 : 
        h, w, _ = array.shape
    else :
        raise 
    
    return QImage(array.data, w, h, 3 * w, QImage.Format_RGB888)

def blendImageWithColorMap(image, label, palette, alpha):
    """ blend image with color map 
    Args: 
        image (3d np.array): RGB image
        label (2d np.array): 1 channel gray-scale image
        pallete (2d np.array) 
        alpha (float)

    Returns: 
        color_map (3d np.array): RGB image
    """

    color_map = np.zeros_like(image)
    
    for idx, color in enumerate(palette) : 
        color_map[label == idx, :] = image[label == idx, :] * alpha + color * (1-alpha)

    return color_map



def points_between(x1, y1, x2, y2):
    """
    coordinate between two points
    """

    d0 = x2 - x1
    d1 = y2 - y1
    
    count = max(abs(d1)+1, abs(d0)+1)

    if d0 == 0:
        return (
            np.full(count, x1),
            np.round(np.linspace(y1, y2, count)).astype(np.int32)
        )

    if d1 == 0:
        return (
            np.round(np.linspace(x1, x2, count)).astype(np.int32),
            np.full(count, y1),  
        )

    return (
        np.round(np.linspace(x1, x2, count)).astype(np.int32),
        np.round(np.linspace(y1, y2, count)).astype(np.int32)
    )
