
from re import L
from PyQt5 import uic
from PyQt5.QtWidgets import *
from ui_design.__import__ import ui_path

brushMenu_ui = 'createNewProject.ui'

form_brushMenu = ui_path(brushMenu_ui)
form_class_brushMenu = uic.loadUiType(form_brushMenu)[0]

class newProjectDialog(QDialog, form_class_brushMenu):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.cancelButton.clicked.connect(self.close)



