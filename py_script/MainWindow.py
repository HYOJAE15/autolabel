import os
import sys

import cv2

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils import resource_path, cvtArrayToQImage, blendImageWithColorMap
from Canvasmodule import Canvas




# Select folder "autolabel"
# MainWindow UI
ui_folder = 'ui_design'
project_folder_ui = 'mainWindow.ui'

form = os.path.join(ui_folder, project_folder_ui)
form_class_main = uic.loadUiType(form)[0]


# Mainwindow class

class MainWindow(QMainWindow, form_class_main) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #### Attributes #### 


        # RoiAutoLabelButton 

        # 단순 모듈화 가 아니라 QToolButton 을 customizing 하여 사용 
        # 아래 사항 은 단순 모듈화 버튼 클릭
        # self.roiAutoLabelButton.clicked.connect(RoiAutoLabelButton.Buttonclicked)


        # Image Blending 
        self.alpha = 0.5

        """
        Pallete for Concrete damage dataset

        background, crack, rebar exposure,
        spalling, efflorescence  
        """
        self.label_palette = np.array([
            [0, 0, 0  ], [255, 0, 0  ], [255, 255, 0],
            [0, 0, 255], [255, 0, 255]
            ])

        # treeview
        self.folderPath = None
        self.pathRoot = QtCore.QDir.rootPath()
        self.treeModel = QFileSystemModel(self)
        self.dialog = QFileDialog()
        self.treeView.clicked.connect(self.treeViewImage)

        # Open folder in treeview 
        self.actionOpenFolder.triggered.connect(self.actionOpenFolderFunction)

        # zoom in and out
        self.scale = 1
        self.zoomInButton.clicked.connect(self.on_zoom_in)
        self.zoomOutButton.clicked.connect(self.on_zoom_out)

        self.mainImageViewer.mousePressEvent = self.getPos



        
    def actionOpenFolderFunction(self) :
        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder")
        self.folderPath = readFolderPath
        self.treeModel.setRootPath(self.folderPath)
        self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
        
        self.treeView.setModel(self.treeModel)
        self.treeView.setRootIndex(self.indexRoot)

    def treeViewImage(self, index) :

        indexItem = self.treeModel.index(index.row(), 0, index.parent())
        imgPath = self.treeModel.filePath(indexItem)
       
        self.img = cv2.imread(imgPath) 
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB) 

        labelPath = imgPath.replace('/leftImg8bit/', '/gtFine/')
        labelPath = labelPath.replace( '_leftImg8bit.png', '_gtFine_labelIds.png')

        self.label = cv2.imread(labelPath, cv2.IMREAD_UNCHANGED) 

        self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
        
        self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        self.scale = self.scrollArea.height() / self.pixmap.height()

        self.resize_image()    

     # method for checking mouse clicks
    def getPos(self, event):

        print('event.pos', event.pos())
        
         
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
        # self.mainImageViewer.resize(scaled_pixmap.width(), scaled_pixmap.height())

    def onChange(self, x):
        alpha = x/100
        dst = cv2.addWeighted(self.cv_img1, 1-alpha, self.cv_img2, alpha, 0) 
        cv2.imshow(self.win_name, dst)




if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainWindow() 
    myWindow.show()
    app.exec_()
