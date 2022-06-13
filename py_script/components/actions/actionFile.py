
import sys
import cv2
import sys

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.utils import *

# MainWindow UI
project_ui = '../../ui_design/mainWindow.ui'

form = resource_path(project_ui)
form_class_main = uic.loadUiType(form)[0]

# ActionFile
class ActionFile :
    def __init__(self) :
        super().__init__()

    def actionOpenFolder(self) :
        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder", "./")
        #readFolderPath = self.dialog.getOpenFileName(self,"select", "./", "Image (*.png *.jpg)" )
        self.folderPath = readFolderPath
        print(f"self.folderPath {self.folderPath}")
        self.treeModel.setRootPath(self.folderPath)
        self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
        
        self.treeView.setModel(self.treeModel)
        self.treeView.setRootIndex(self.indexRoot)
        

    def actionCreateProject(self):
        pass

    def actionOpenProject(self):
        pass

    # def treeViewImage(self, index) :

    #     indexItem = self.treeModel.index(index.row(), 0, index.parent())
    #     imgPath = self.treeModel.filePath(indexItem)
       
    #     self.img = cv2.imread(imgPath) 
    #     self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB) 

    #     labelPath = imgPath.replace('/leftImg8bit/', '/gtFine/')
    #     labelPath = labelPath.replace( '_leftImg8bit.png', '_gtFine_labelIds.png')

    #     self.label = cv2.imread(labelPath, cv2.IMREAD_UNCHANGED) 
    #     self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
        
    #     self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
    #     self.scale = self.scrollArea.height() / self.pixmap.height()

    #     self.resize_image()  

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = ActionFile() 
    myWindow.show()
    app.exec_()
