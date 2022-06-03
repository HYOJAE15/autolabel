from lib2to3.pytree import type_repr
import sys

import cv2

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils import *

import sys 
from brushMenuDialog import BrushMenu

sys.path.append("./dnn/mmseg")

from mmseg.apis import init_segmentor, inference_segmentor


# Select folder "autolabel"
# MainWindow UI
project_ui = '../ui_design/mainWindow.ui'

form = resource_path(project_ui)
form_class_main = uic.loadUiType(form)[0]

brushMenu_ui = '../ui_design/brushMenuDialog.ui'

form_brushMenu = resource_path(brushMenu_ui)
form_class_brushMenu = uic.loadUiType(form_brushMenu)[0]
# Mainwindow class

class MainWindow(QMainWindow, form_class_main) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #### Attributes #### 
    
        self.brushSize = 1
        self.ver_scale = 1
        self.hzn_scale = 1
        self.x = 0 
        self.y = 0 
        self.label_class = 0
        self.alpha = 0.5
        self.use_brush = False
        self.set_roi = False

        # config_file = './dnn/mmseg/configs/cgnet_512x512_60k_CrackAsCityscapes.py'
        # checkpoint_file = './dnn/mmseg/checkpoints/crack_cgnet_2048x2048_iter_60000.pth'

        # self.model = init_segmentor(config_file, checkpoint_file, device='cuda:0')

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
        self.BrushMenu = QMenu()
        self.brushButton.setMenu(self.BrushMenu)
        #self.brushButton.clicked.connect(self.showBrushMenu)
        self.brushButton.clicked.connect(self.openBrushDialog)

        # self.brushButton.clicked.connect(self.updateBrushState)
        self.mainImageViewer.mousePressEvent = self.mousePressEvent
        self.mainImageViewer.mouseMoveEvent = self.mouseMoveEvent
        self.mainImageViewer.mouseReleaseEvent = self.mouseReleaseEvent

        # auto label tools 
        self.roiMenu = QMenu()
        self.roiMenu.addAction("256*256", self.roi256)
        self.roiMenu.addAction("Set Rectangle", self.roiRec)
        self.roiAutoLabelButton.setMenu(self.roiMenu)
        self.roiAutoLabelButton.clicked.connect(self.showRoiMenu)
        #self.roiAutoLabelButton.clicked.connect(self.runRoiAutoLabel)

        # listWidget
        self.listWidget.itemClicked.connect(self.getListWidgetIndex)

        # label opacity
        self.lableOpacitySlider.valueChanged.connect(self.showHorizontalSliderValue)

        # openFolder 메뉴를 클릭 했을 때 getopenfilename 으로 파일 을 불러오고 그 해당 현재 주소를 가지고 
        # treeview 생성??
    
    def openBrushDialog(self):
        self.use_brush = True
        self.brushMenu = BrushMenu()
        self.brushMenu.horizontalSlider.valueChanged.connect(self.setBrushSize)
        self.brushMenu.exec_()
    
    def setBrushSize(self):
        self.brushSize = self.brushMenu.brushSize

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

        x, y = self.applyBrushSize(x, y)

        try : 
            self.label[y, x] = self.label_class 
            self.colormap[y, x] = self.img[y, x] * self.alpha + self.label_palette[self.label_class] * (1-self.alpha)
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        except BaseException as e : 
            print(e)


    def applyBrushSize(self, X, Y): 

        circle = False

        width = int(self.brushSize / 2)
        
        return_x = []
        return_y = []

        _Y, _X = np.mgrid[-width:width, -width:width]
        _Y, _X = _Y.flatten(), _X.flatten()
        _Y, _X = np.squeeze(_Y), np.squeeze(_X)

        if circle :
            dist = [np.sqrt(_x**2 + _y**2) for _x, _y in zip(_Y, _X)]
            _Y =  [_y for idx, _y in enumerate(_Y) if dist[idx] < width]
            _X = [_x for idx, _x in enumerate(_X) if dist[idx] < width]
            _X, _Y = np.array(_X), np.array(_Y)

        for x, y in zip(X, Y):
            _x = x + _X
            _y = y + _Y
            return_x += _x.tolist()
            return_y += _y.tolist()

        return return_x, return_y

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
        

    def showBrushMenu(self) :
        
        self.brushButton.showMenu()
        
    def updateBrushState(self):
        
        self.use_brush = 1 - self.use_brush
        # 효재: 자료형에서 int 형과 bool 형 차이 없이 '0'(int)이면 False(bool)인가??
        # 병현: 응 맞아 ㅋㅋ 
        print(f"type_self.use_brush {type(self.use_brush)}")
        print(f"self.use_brush {self.use_brush}")
        print(f"self.set_roi {self.set_roi}")
         

    def brushPressOrReleasePoint(self, event):

        x, y = getScaledPoint(event, self.scale)
        
        if (self.x != x) or (self.y != y) :
             
            self.updateLabelandColormap([x], [y])
            self.resize_image()  
            self.x, self.y = x, y


    def brushMovingPoint(self, event):

        x, y = getScaledPoint(event, self.scale)
        
        if (self.x != x) or (self.y != y) : 

            x_btw, y_btw = points_between(self.x, self.y, x, y)

            self.updateLabelandColormap(x_btw, y_btw)
            self.resize_image()  
            self.x, self.y = x, y


    def showRoiMenu(self):
        self.roiAutoLabelButton.showMenu()

    def roi256(self):
        print("roi256")
        self.brushButton.setChecked(False)
        self.roiAutoLabelButton.setChecked(True)

        self.use_brush = False

        self.set_roi = True


    def roiRec(self):
        self.brushButton.setChecked(False)
        self.roiAutoLabelButton.setChecked(True)
        print(f"self.use_brush {self.use_brush}")

        self.use_brush = False

        self.set_roi = True

        print(f"self.set_roi {self.set_roi}")
        print(f"self.use_brush {self.use_brush}")
        
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
