
from re import L
from PyQt5 import uic
from PyQt5.QtWidgets import *
from utils.utils import *

brushMenu_ui = '../../ui_design/setCategoryInfo.ui'

form_brushMenu = resource_path(brushMenu_ui)
form_class_brushMenu = uic.loadUiType(form_brushMenu)[0]

class setCategoryDialog(QDialog, form_class_brushMenu):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.show()

        self.cancelButton.clicked.connect(self.close)


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = setCategoryDialog() 
    myWindow.show()
    app.exec_()
