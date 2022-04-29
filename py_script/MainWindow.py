import sys
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import uic
import os 

def resource_path(relative_path): 
    """ Get absolute path to resource, works for dev and for PyInstaller """ 
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)
# import os, import sys  한다음 위 함수 정의 해서 pyinstaller 오류 해결


# UI파일 연결, MainWindow 열고 각 menu 들은 Dialog 로 실행 
# mainwind.ui 에서 각 메뉴의 Dialog창을 띄운다.
# MainWindow ui
form_main = resource_path("../ui_design/mainwind.ui")
form_class_main = uic.loadUiType(form_main)[0]
# ToolsDialog
form_tools = resource_path("../ui_design/toolsdial.ui")
form_class_tools = uic.loadUiType(form_tools)[0]
# 


# menu optiondialog
# ToolsDialog
class ToolsDialog(QDialog, form_class_tools) :
    def __init__(self, parent) :
        super().__init__(parent)
        self.setupUi(self)
        self.show()



# Mainwindow
class MainWindow(QMainWindow, form_class_main) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        
        # menubar action
        self.actionTools.triggered.connect(self.actionToolsFunction)


    def actionToolsFunction(self) :
        ToolsDialog(self)  





if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainWindow() 
    myWindow.show()
    app.exec_()