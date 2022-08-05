import sys
import cv2

import json
import os


import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


from utils.utils import *


from components.actions.actionFile import ActionFile

from components.buttons.autoLabelButton import AutoLabelButton
from components.buttons.brushButton import BrushButton
from components.buttons.eraseButton import EraseButton
from components.buttons.zoomButton import ZoomButton

from components.dialogs.brushMenuDialog import BrushMenu
from components.dialogs.eraseMenuDialog import EraseMenu
from components.dialogs.newProjectDialog import newProjectDialog
from components.dialogs.setCategoryDialog import setCategoryDialog

from components.opener.dialogOpener import dialogOpener

from components.widgets.treeView import TreeView


sys.path.append("./dnn/mmsegmentation")
from mmseg.apis import init_segmentor


# Select folder "autolabel"
# MainWindow UI
project_ui = '../../ui_design/mainWindow.ui'

form = resource_path(project_ui)
form_class_main = uic.loadUiType(form)[0]

# Mainwindow class

class Painter :
    def __init__(self) :
        super().__init__()

        

    #### Methods ##### 

    ######################## 
    ### Image Processing ###
    ########################

    
    def updateLabelandColormap(self, x, y):
        
        if self.use_brush :
            x, y = self.applyBrushSize(x, y)
        elif self.use_erase :
            x, y = self.applyEraseSize(x, y)


        try : 
            print(f"label_class {self.label_class}")
            print(type(self.label_class))
            if self.use_brush :
                self.label[y, x] = self.label_class
                self.colormap[y, x] = self.img[y, x] * self.alpha + self.label_palette[self.label_class] * (1-self.alpha)

            elif self.use_erase :
                self.label[y, x] = 0
                print("eraseMode")
                self.colormap[y, x] = self.img[y, x] * self.alpha + self.label_palette[0] * (1-self.alpha)

            
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        except BaseException as e : 
            print(e)

    
    
    def resize_image(self):
        size = self.pixmap.size()
        self.scaled_pixmap = self.pixmap.scaled(self.scale * size)
        self.mainImageViewer.setPixmap(self.scaled_pixmap)

    def showHorizontalSliderValue(self):

        self.labelOpacityCheckBox.setChecked(True)

        if abs(self.alpha-(self.lableOpacitySlider.value() / 100)) > 0.03 :
            self.alpha = self.lableOpacitySlider.value() / 100
            self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
            self.resize_image()    

    def labelOpacityOnOff(self):
        
        if self.labelOpacityCheckBox.isChecked():
            self.alpha = self.lableOpacitySlider.value() / 100
        else : 
            self.alpha = 1 
        
        self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
        self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        self.resize_image()    
