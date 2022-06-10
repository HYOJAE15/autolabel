
import sys
import cv2
import sys

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.utils import *

# Mainwindow class
class ZoomButton :
    def __init__(self) :
        super().__init__()
       
    def on_zoom_in(self):
        self.scale *= 2
        self.resize_image()

    def on_zoom_out(self):
        self.scale /= 2
        self.resize_image()


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = ZoomButton() 
    myWindow.show()
    app.exec_()
