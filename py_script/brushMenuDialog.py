import sys

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import *
from utils import *

brushMenu_ui = '../ui_design/brushMenuDialog.ui'

form_brushMenu = resource_path(brushMenu_ui)
form_class_brushMenu = uic.loadUiType(form_brushMenu)[0]

class BrushMenu(QDialog, form_class_brushMenu):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.use_brush = True
        self.brushSize = 1
        #self.horizontalSlider.setValue(self.brushSize)
        self.lineEdit.setText(f'{self.brushSize} px')
        self.horizontalSlider.valueChanged.connect(self.changeSliderValueText)
        #self.brushSize = self.horizontalSlider.value()
        #self.lineEdit.setText(f'{self.brushSize} px') 

    def changeSliderValueText(self):
        self.brushSize = self.horizontalSlider.value()
        self.lineEdit.setText(f'{self.brushSize} px')

    def keyPressEvent(self, event):
        # print(event.key())
        if event.key() in [16777220, 16777221] : 
            # print('Enter pressed')
            self.changeBrushSizeAndSliderBar()
        else:
            super().keyPressEvent(event)

    def changeBrushSizeAndSliderBar(self):
        txt = self.lineEdit.text()
        numbers = [int(s) for s in txt.split() if s.isdigit()]
        if numbers : 
            self.brushSize = numbers[0]
            self.lineEdit.setText(f'{self.brushSize} px') 
            self.horizontalSlider.setValue(self.brushSize) 

