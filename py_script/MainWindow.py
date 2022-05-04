import os
import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QTreeView,QFileSystemModel,QApplication
from PyQt5 import uic

def resource_path(relative_path): 
    """ Get absolute path to resource, works for dev and for PyInstaller """ 
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)
# import os, import sys  한다음 위 함수 정의 해서 pyinstaller 오류 해결


# UI파일 연결, MainWindow 열고 각 menu 들은 Dialog 로 실행 
# mainwind.ui 에서 각 메뉴의 Dialog창을 띄운다.

# MainWindow
form_main = resource_path("../ui_design/mainwind.ui")
form_class_main = uic.loadUiType(form_main)[0]

# ToolsDialog
form_tools = resource_path("../ui_design/toolsdial.ui")
form_class_tools = uic.loadUiType(form_tools)[0]

# ImageDialog
form_image = resource_path("../ui_design/imagedial.ui")
form_class_image = uic.loadUiType(form_image)[0]


# menu
# ToolsDialog
class ToolsDialog(QDialog, form_class_tools) :
    def __init__(self, parent) :
        super().__init__(parent)
        self.setupUi(self)
        self.show()

# ImageDialog, when imagefile open
# 이미지 사이즈 대로 출력한다.
class ImageDialog(QDialog, form_class_image) :
    def __init__(self, parent) :
        super().__init__(parent)
        self.setupUi(self)
        self.show()

        # ImageDialog : 내부 버튼 
        self.btn_img_op.clicked.connect(self.btn_img_opFunction)
    # ImageDialog 내부 버튼 클릭시  
    # 사진 사이즈 대로 pixmap resize 하고 그에 맞게 label 이 조정 되면서 사진 크기 에 맞게 출력 된다
    def btn_img_opFunction(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file','/', "Image files (*.jpg *.png)")
        imagePath = fname[0]
        pixmap = QPixmap(imagePath)
        self.label.setPixmap(QPixmap(pixmap))
        self.resize(pixmap.width(), pixmap.height())



# Mainwindow

class MainWindow(QMainWindow, form_class_main) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # scroll area 
        self.scroll = QScrollArea

        
        # treeview
        self.folderPath = None
        self.pathRoot = QtCore.QDir.rootPath()
        self.treeModel = QFileSystemModel(self)
        self.dialog = QFileDialog()

        # menubar action
        self.actionTools.triggered.connect(self.actionToolsFunction)
        self.actionOpen.triggered.connect(self.actionOpenFunction)
        self.actionOpenImage.triggered.connect(self.actionOpenImageFunction)
        self.actionOpenFolder.triggered.connect(self.actionOpenFolderFunction)

    # menubar action Function

    def actionToolsFunction(self) :
        ToolsDialog(self)  

    def actionOpenFunction(self) :
        ImageDialog(self)

    # 메뉴바의 openimage 클릭시 mainimageviewer 에 이미지를 보여준다
    def actionOpenImageFunction(self) :
        filename = QFileDialog.getOpenFileName(self, 'open image', 'C:/', 'images (*.jpg *.psd *.png)')
        imagepath = filename[0]
        pixmap = QPixmap(imagepath)
        self.mainImageViewer.setPixmap(QPixmap(pixmap))
        

    # 메뉴바 의 openfolder 클릭시 treeview 에 해당 폴더를 보여준다
    def actionOpenFolderFunction(self) :
        readFolderPath = self.dialog.getExistingDirectory(self, "Select Folder")
        self.folderPath = readFolderPath
        self.treeModel.setRootPath(self.folderPath)
        self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
        
        self.treeView.setModel(self.treeModel)
        self.treeView.setRootIndex(self.indexRoot)




if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainWindow() 
    myWindow.show()
    app.exec_()