
from email import utils
import sys
import cv2
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.utils import *

class TreeView() :
    def __init__(self) :
        super().__init__()

    
    ######################## 
    ### Folder Tree View ###
    ########################

    def actionOpenFolderFunction(self) :
        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder", "./")
        #readFolderPath = self.dialog.getOpenFileName(self,"select", "./", "Image (*.png *.jpg)" )
        self.folderPath = readFolderPath
        print(f"self.folderPath {self.folderPath}")
        self.treeModel.setRootPath(self.folderPath)
        self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
        
        self.treeView.setModel(self.treeModel)
        self.treeView.setRootIndex(self.indexRoot)


    def treeViewImage(self, index) :

        try : 

            indexItem = self.treeModel.index(index.row(), 0, index.parent())
            
            self.imgPath = self.treeModel.filePath(indexItem)
            print(f"self.imgPath {self.imgPath}")
            dotSplit_imgPath = self.imgPath.split('.')
            print(dotSplit_imgPath)
            
            if 'png' in dotSplit_imgPath :

                self.img = cv2.imread(self.imgPath) 
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB) 

                self.labelPath = self.imgPath.replace('/leftImg8bit/', '/gtFine/')
                self.labelPath = self.labelPath.replace( '_leftImg8bit.png', '_gtFine_labelIds.png')

                self.label = cv2.imread(self.labelPath, cv2.IMREAD_UNCHANGED) 
                print('self.label shape', self.label.shape)
                self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
            
                self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
                self.scale = self.scrollArea.height() / self.pixmap.height()

                self.resize_image()

            else :
                pass
              
        
        except: 
            print("Error Occured")
    
