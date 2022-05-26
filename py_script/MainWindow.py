import sys

import cv2

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils import *

import sys 

sys.path.append("./dnn/mmseg")

from mmseg.apis import init_segmentor, inference_segmentor

# git test - 1
# git test - 2


# Select folder "autolabel"
# MainWindow UI
project_ui = '../ui_design/mainWindow.ui'

form = resource_path(project_ui)
form_class_main = uic.loadUiType(form)[0]

# Mainwindow class

class MainWindow(QMainWindow, form_class_main) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #### Attributes #### 
    
        self.brushSize = 28
        self.ver_scale = 1
        self.hzn_scale = 1
        self.x = 0 
        self.y = 0 
        self.label_class = 0
        self.alpha = 0.5
        self.use_brush = False
        self.set_roi = False

        config_file = './dnn/mmseg/configs/cgnet_512x512_60k_CrackAsCityscapes.py'
        checkpoint_file = './dnn/mmseg/checkpoints/crack_cgnet_2048x2048_iter_60000.pth'

        self.model = init_segmentor(config_file, checkpoint_file, device='cuda:0')

        """
        Pallete for Concrete damage dataset

        background, crack, rebar exposure,
        spalling, efflorescence  
        """
        self.label_palette = np.array([
            [0, 0, 0  ], [255, 0, 0  ], [255, 255, 0],
            [0, 0, 255], [255, 0, 255]
            ])

        # treeview setting 
        self.folderPath = None
        self.pathRoot = QtCore.QDir.rootPath()
        self.treeModel = QFileSystemModel(self)
        self.dialog = QFileDialog()

        #### Methods ##### 

        # treeview
        self.treeView.clicked.connect(self.treeViewImage)
        self.actionOpenFolder.triggered.connect(self.actionOpenFolderFunction)

        # zoom in and out
        self.scale = 1
        self.zoomInButton.clicked.connect(self.on_zoom_in)
        self.zoomOutButton.clicked.connect(self.on_zoom_out)

        # brush tools
        self.brushButton.clicked.connect(self.updateBrushState)
        self.mainImageViewer.mousePressEvent = self.mousePressEvent
        self.mainImageViewer.mouseMoveEvent = self.mouseMoveEvent
        self.mainImageViewer.mouseReleaseEvent = self.mouseReleaseEvent

        # auto label tools 
        self.roiAutoLabelButton.clicked.connect(self.runRoiAutoLabel)

        # listWidget
        self.listWidget.itemClicked.connect(self.getListWidgetIndex)

        # label opacity
        self.lableOpacitySlider.valueChanged.connect(self.showHorizontalSliderValue)

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

    def updateLabelandColormap(self, x, y):
        
        self.label[y, x] = self.label_class 
        self.colormap[y, x] = self.img[y, x] * self.alpha + self.label_palette[self.label_class] * (1-self.alpha)
        self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))

    

    def mousePressEvent(self, event):

        if self.use_brush : 
            self.brushPressOrReleasePoint(event)

        elif self.set_roi : 
            self.roiPressPoint(event)

    def mouseMoveEvent(self, event):

        if self.use_brush : 
            self.brushMovingPoint(event)

        elif self.set_roi : 
            self.roiMovingPoint(event)

    def mouseReleaseEvent(self, event): 

        if self.use_brush : 
            self.brushPressOrReleasePoint(event)

        elif self.set_roi : 
            self.roiReleasePoint(event)

        
    def updateBrushState(self):
        
        self.use_brush = 1 - self.use_brush
        
            
    def brushPressOrReleasePoint(self, event):

        x, y = getScaledPoint(event, self.scale)
        
        if (self.x != x) or (self.y != y) : 

            self.updateLabelandColormap(x, y)
            self.resize_image()  
            self.x, self.y = x, y


    def brushMovingPoint(self, event):

        x, y = getScaledPoint(event, self.scale)
        
        if (self.x != x) or (self.y != y) : 

            x_btw, y_btw = points_between(self.x, self.y, x, y)

            self.updateLabelandColormap(x_btw, y_btw)
            self.resize_image()  
            self.x, self.y = x, y


    def runRoiAutoLabel(self, event):
        self.brushButton.setChecked(False)
        self.use_brush = False

        self.set_roi = True
        
    def roiPressPoint(self, event):

        x, y = getScaledPoint(event, self.scale)

        self.rect_start = x, y

    def roiMovingPoint(self, event):

        x, y = getScaledPoint(event, self.scale)

        self.rect_end = x, y

        thickness = 5

        rect_hover = cv2.rectangle(
            self.colormap.copy(), self.rect_start, self.rect_end, (255, 255, 255), thickness) # , color, thickness, lineType,)
        self.pixmap = QPixmap(cvtArrayToQImage(rect_hover))
        self.resize_image()
        

    def roiReleasePoint(self, event):

        x, y = getScaledPoint(event, self.scale)

        self.rect_end = x, y

        result = inference_segmentor(self.model, self.img[self.rect_start[1]: y, self.rect_start[0]: x, :])

        idx = np.argwhere(result[0] == 1)
        y_idx, x_idx = idx[:, 0], idx[:, 1]
        x_idx = x_idx + self.rect_start[0]
        y_idx = y_idx + self.rect_start[1]

        self.label[y_idx, x_idx] = 1
        
        self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
        self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        self.resize_image()
        

    def setVerticalScale(self, new_scale):
        self.ver_scale = new_scale

    def setHorizontalScale(self, new_scale):
        self.hzn_scale = new_scale

    def on_zoom_in(self):
        self.scale *= 2
        self.resize_image()

    def on_zoom_out(self):
        self.scale /= 2
        self.resize_image()

    def resize_image(self):
        size = self.pixmap.size()
        self.scaled_pixmap = self.pixmap.scaled(self.scale * size)
        self.mainImageViewer.setPixmap(self.scaled_pixmap)

    def showHorizontalSliderValue(self):

        if abs(self.alpha-(self.lableOpacitySlider.value() / 100)) > 0.03 :
            self.alpha = self.lableOpacitySlider.value() / 100
            self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
            self.resize_image()    

    def getListWidgetIndex (self):

        print(f"self.listWidget.currentRow(){self.listWidget.currentRow()}")
        
        self.label_class = self.listWidget.currentRow()


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainWindow() 
    myWindow.show()
    app.exec_()
