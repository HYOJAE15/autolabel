import os
import sys

from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *


def resource_path(relative_path): 
    """ Get absolute path to resource, works for dev and for PyInstaller """ 
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)
# import os, import sys  한다음 위 함수 정의 해서 pyinstaller 오류 해결


# UI파일 연결, MainWindow 열고 각 menu 들은 Dialog 로 실행 
# mainwind.ui 에서 각 메뉴의 Dialog창을 띄운다.

# MainWindow UI
form_main = resource_path("../ui_design/mainwind.ui")
form_class_main = uic.loadUiType(form_main)[0]




# Mainwindow class

class MainWindow(QMainWindow, form_class_main) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

    
        
        # treeview
        self.folderPath = None
        self.pathRoot = QtCore.QDir.rootPath()
        self.treeModel = QFileSystemModel(self)
        self.dialog = QFileDialog()
        self.treeView.clicked.connect(self.treeViewImage)


        # file 메뉴 
        self.actionOpenImage.triggered.connect(self.actionOpenImageFunction)
        self.actionOpenFolder.triggered.connect(self.actionOpenFolderFunction)

        # zoom in and out
        self.scale = 1
        self.zoomInButton.clicked.connect(self.on_zoom_in)
        self.zoomOutButton.clicked.connect(self.on_zoom_out)

        # Brush
        #self.brushButton.clicked.connect(self.burshFunction)

       




    # menubar action Function

    # 메뉴바의 openimage 클릭시 mainimageviewer 에 이미지를 보여준다
    def actionOpenImageFunction(self) :
        filename = QFileDialog.getOpenFileName(self, 'open image', 'C:/', 'images (*.jpg *.psd *.png)')
        imagepath = filename[0]
        pixmap = QPixmap(imagepath)
        self.mainImageViewer.setPixmap(QPixmap(pixmap))
        

    # 메뉴바 의 openfolder 클릭시 treeview 에 해당 폴더를 보여준다, treeview function
    def actionOpenFolderFunction(self) :
        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder")
        self.folderPath = readFolderPath
        self.treeModel.setRootPath(self.folderPath)
        self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
        
        self.treeView.setModel(self.treeModel)
        self.treeView.setRootIndex(self.indexRoot)

    # treeview 에서 파일 클릭 시 클릭된 파일 로드 
    # 이미지 파일 클릭시 묶여있는 라벨링 이미지 와 함께 불러와 합성후 하나의 파일로 만들어 보여준다
    @pyqtSlot(QModelIndex)
    def treeViewImage(self, index) :

        indexItem = self.treeModel.index(index.row(), 0, index.parent())
        filePath = self.treeModel.filePath(indexItem)

        self.pixmap = QPixmap(filePath) 
        # self.original_image = QPixmap(org_img_filePath) # original image path
        # self.label_image = QPixmap(lab_img_filePath) # label image path
        # self.pallette 
        # self.color_image 

        # blend 
        # self.blendid_image = self.org_img * 0.7 + self.label * 0.3

        self.scale = self.mainImageViewer.height() / self.pixmap.height()
        self.resize_image()


    def on_zoom_in(self, event):
        self.scale *= 2
        self.resize_image()

    def on_zoom_out(self, event):
        self.scale /= 2
        self.resize_image()

    def resize_image(self):
        
        size = self.pixmap.size()
        scaled_pixmap = self.pixmap.scaled(self.scale * size)
        self.mainImageViewer.setPixmap(scaled_pixmap)
    
    
    # 투명도 조절 함수 
    # def change_opacity 
        # op_change_image = TWE$R^#$@%^
        # self.mainImageViewer.setPixmap(op_change_image)




if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainWindow() 
    myWindow.show()
    app.exec_()
