
from PyQt5 import uic
from PyQt5.QtWidgets import *
from ui_design.__import__ import load_ui

ui = load_ui('createNewProject.ui')

class newProjectDialog(QDialog, ui):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.cancelButton.clicked.connect(self.close)



