
import sys
import cv2
import sys

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.utils import *

# Select folder "autolabel"
# MainWindow UI
project_ui = '../../ui_design/mainWindow.ui'

form = resource_path(project_ui)
form_class_main = uic.loadUiType(form)[0]

# Mainwindow class
class AutoLabelButton :
    def __init__(self) :
        pass

        
    
if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = AutoLabelButton() 
    myWindow.show()
    app.exec_()
