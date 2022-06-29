
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
        self.scale *= 1.5
        self.resize_image()
        self.relativeMouseCoordX = QCursor.pos().x
        self.relativeMouseCoordY = QCursor.pos().y
        print(self.relativeMouseCoordX, self.relativeMouseCoordY)

        # self.scrollArea.verticalScrollBar().setValue(0)
        # self.scrollArea.horizontalScrollBar().setValue(0)


    def on_zoom_out(self):
        self.scale /= 1.5
        self.resize_image()

        self.relativeMouseCoordX = QCursor.pos().x
        self.relativeMouseCoordY = QCursor.pos().y
        print(self.relativeMouseCoordX, self.relativeMouseCoordY)

        # print(self.scrollArea.verticalScrollBar().maximum())
        # print(self.scrollArea.horizontalScrollBar().maximum())
        # print(self.scrollArea.verticalScrollBar().value())
        # print(self.scrollArea.horizontalScrollBar().value())
        # self.scrollArea.verticalScrollBar().setValue(0)
        # self.scrollArea.horizontalScrollBar().setValue(0)

