
from PyQt5 import uic
from PyQt5.QtWidgets import *
from numpy import number
from ui_design.__import__ import ui_path

eraseMenu_ui = 'eraseMenuDialog.ui'

form_eraseMenu = ui_path(eraseMenu_ui)
form_class_eraseMenu = uic.loadUiType(form_eraseMenu)[0]

class EraseMenu(QDialog, form_class_eraseMenu):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.erasehorizontalSlider.valueChanged.connect(self.eraseChangeSliderValueText)


    def eraseChangeSliderValueText(self):
        number = self.erasehorizontalSlider.value()

        if number % 2 == 1:
            
            number += 1

        self.eraseSize = number
        self.eraselineEdit.setText(f'{number} px')
            

    def keyPressEvent(self, event):
        if event.key() in [16777220, 16777221] : # enter key code
            self.eraseChangeBrushSizeAndSliderBar()
        else:
            super().keyPressEvent(event)

    def eraseChangeBrushSizeAndSliderBar(self):
        txt = self.eraselineEdit.text()
        numbers = [int(s) for s in txt.split() if s.isdigit()]
        number = numbers[0]
        if number : 
            if number < 2: 
                number = 2
            elif number > 50: # change it to max number 
                number = 50

            if (number % 2) == 1:
                number += 1

            self.eraseSize = number
            self.eraselineEdit.setText(f'{self.eraseSize} px') 
            self.erasehorizontalSlider.setValue(self.eraseSize) 