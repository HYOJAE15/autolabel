
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
        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder")
        #readFolderPath = self.dialog.getOpenFileName(self,"select", "./", "Image (*.png *.jpg)" )
        self.folderPath = readFolderPath
        print(f"self.folderPath {self.folderPath}")
        self.fileNameLabel.setText(self.folderPath)
        slashSplit_imgPath = self.folderPath.split('/')
        print(slashSplit_imgPath)
        cityScapeDataset_folderPath = os.path.basename(self.folderPath)
        print(os.path.basename(self.folderPath))

        if "leftImg8bit" in slashSplit_imgPath and cityScapeDataset_folderPath in ["train", "val", "test"] :
            self.openFolderPath = self.folderPath
            print(f"cityscapedataset 준수 {self.openFolderPath}")

        else :
            self.openFolderPath = None
            print(f"cityscapedataset 비준수 {self.openFolderPath}")


        self.treeModel.setRootPath(self.folderPath)
        self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
        
        self.treeView.setModel(self.treeModel)
        self.treeView.setRootIndex(self.indexRoot)
        print(self.openFolderPath)
        


    def treeViewImage(self, index) :

        try : 
            
            indexItem = self.treeModel.index(index.row(), 0, index.parent())
            
            self.imgPath = self.treeModel.filePath(indexItem)
            print(f"self.imgPath {self.imgPath}")
            self.fileNameLabel.setText(self.imgPath)
            dotSplit_imgPath = self.imgPath.split('.')
            print(dotSplit_imgPath)
            
            if 'png' in dotSplit_imgPath :

                self.img = cv2.imdecode(np.fromfile(self.imgPath, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB) 

                self.labelPath = self.imgPath.replace('/leftImg8bit/', '/gtFine/')
                self.labelPath = self.labelPath.replace( '_leftImg8bit.png', '_gtFine_labelIds.png')

                self.label = cv2.imdecode(np.fromfile(self.labelPath, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                print('self.label shape', self.label.shape)
                self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
            
                self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
                self.scale = self.scrollArea.height() / self.pixmap.height()

                self.resize_image()

                self.situationLabel.clear()
                self.saveImgName = None
                self.brushMemory = None

                

            else :
                pass
              
        
        except: 
            print("Error Occured")
    


    def askSave(self) :
        
        print("askSave")
        
