
from PyQt5 import uic
from PyQt5.QtWidgets import *
from numpy import number
from utils.utils import *

brushMenu_ui = '../../ui_design/brushMenuDialog.ui'

form_brushMenu = resource_path(brushMenu_ui)
form_class_brushMenu = uic.loadUiType(form_brushMenu)[0]

class BrushMenu(QDialog, form_class_brushMenu):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.use_brush = True
        # self.brushSize = 2
        #self.horizontalSlider.setValue(self.brushSize)
        #self.lineEdit.setText(f'{self.brushSize} px')
        self.horizontalSlider.valueChanged.connect(self.changeSliderValueText)
        #self.brushSize = self.horizontalSlider.value()
        #self.lineEdit.setText(f'{self.brushSize} px') 
        # print(self.brushSize)
        


    def changeSliderValueText(self):
        number = self.horizontalSlider.value()

        if number % 2 == 1:
            
            number += 1

        self.brushSize = number
        print(self.brushSize)
        self.lineEdit.setText(f'{number} px')
        #self.horizontalSlider.setValue(self.brushDialogNumber) 
            

    def keyPressEvent(self, event):
        if event.key() in [16777220, 16777221] : # enter key code
            self.changeBrushSizeAndSliderBar()
        else:
            super().keyPressEvent(event)

    def changeBrushSizeAndSliderBar(self):
        txt = self.lineEdit.text()
        numbers = [int(s) for s in txt.split() if s.isdigit()]
        number = numbers[0]
        if number : 
            if number < 2: 
                number = 2
            elif number > 50: # change it to max number 
                number = 50

            if (number % 2) == 1:
                number += 1

            self.brushSize = number
            self.lineEdit.setText(f'{self.brushSize} px') 
            self.horizontalSlider.setValue(self.brushSize) 

