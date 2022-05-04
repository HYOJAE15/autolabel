from PyQt5.QtWidgets import QTreeView,QFileSystemModel,QApplication
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtCore

from PyQt5 import uic

class treeWidgetC():
    def __init__(self) :
        super().__init__()

        self.pathRoot = QtCore.QDir.rootPath()

        self.treeModel = QFileSystemModel(self)
        self.dialog = QFileDialog()
    
        self.folder.triggered.connect(self.openFolder)

    
    def openFolder(self):
        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder")
        self.folderPath = readFolderPath
        self.treeModel.setRootPath(self.folderPath)
        self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
        
        self.treeView.setModel(self.treeModel)
        self.treeView.setRootIndex(self.indexRoot)



