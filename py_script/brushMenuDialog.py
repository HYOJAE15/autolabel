import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from utils import *

brushMenu_ui = '../ui_design/brushMenuDialog.ui'

form_brushMenu = resource_path(brushMenu_ui)
form_class_brushMenu = uic.loadUiType(form_brushMenu)[0]


class BrushMenu(QDialog, form_class_brushMenu):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.show()


    




if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = BrushMenu() 
    myWindow.show()
    app.exec_()
