import os
import sys 

from PyQt5.QtWidgets import QTreeView,QFileSystemModel,QApplication
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtCore

from PyQt5 import uic
from utils import resource_path


ui_folder = 'ui_design'
project_folder_ui = 'project_folder.ui'

form = os.path.join(ui_folder, project_folder_ui)
form_class = uic.loadUiType(form)[0]


class WindowClass(QMainWindow, form_class):
    def __init__(self) : 
        super().__init__()

        self.setupUi(self)
        self.folderPath = None
        self.pathRoot = QtCore.QDir.rootPath()

        self.treeModel = QFileSystemModel(self)
        self.dialog = QFileDialog()
    
        self.actionOpen_Folder.triggered.connect(self.openFolder)

    
    def openFolder(self):
        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder")
        self.folderPath = readFolderPath
        self.treeModel.setRootPath(self.folderPath)
        self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
        
        self.treeView.setModel(self.treeModel)
        self.treeView.setRootIndex(self.indexRoot)


    
    

        

    




if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()