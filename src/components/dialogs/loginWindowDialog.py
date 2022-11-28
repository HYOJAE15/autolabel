

from PyQt5.QtWidgets import *
from ui_design.__import__ import load_ui

ui = load_ui('loginDialog.ui')

class LoginWindow(QDialog, ui):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        
        self.horizontalSlider.valueChanged.connect(self.changeSliderValueText)