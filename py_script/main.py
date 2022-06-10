
import sys
import cv2
import sys

import numpy as np 

from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.utils import *

from components.dialogs.brushMenuDialog import BrushMenu
from components.dialogs.newProjectDialog import newProjectDialog
from components.dialogs.setCategoryDialog import setCategoryDialog

from components.buttons.autoLabelButton import AutoLabelButton
from components.buttons.brushButton import BrushButton
from components.buttons.zoomButton import ZoomButton

from components.actions.actionFile import ActionFile

from components.widgets.treeView import TreeView

project_ui = '../../ui_design/mainWindow.ui'
form = resource_path(project_ui)
form_class_main = uic.loadUiType(form)[0]

# Mainwindow class
class MainWindow(QMainWindow, form_class_main, 
    AutoLabelButton, BrushButton, ZoomButton,
    ActionFile, TreeView) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #### Attributes #### 
    
        self.brushSize = 2
        self.ver_scale = 1
        self.hzn_scale = 1
        self.x = 0 
        self.y = 0 
        self.label_class = 0
        self.alpha = 0.5
        self.use_brush = False
        self.set_roi = False
        self.circle = True

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

        # 1. Menu
        
        self.treeView.clicked.connect(self.treeViewImage)
        self.actionOpenFolder.triggered.connect(self.actionOpenFolderFunction)

        self.actionNewProject.triggered.connect(self.openNewProjectDialog)
        # self.actionCreate_a_Project.triggered.connect(self.openCreateProjectDialog)

        # 2. Zoom in and out
        self.scale = 1
        self.zoomInButton.clicked.connect(self.on_zoom_in)
        self.zoomOutButton.clicked.connect(self.on_zoom_out)

        # 3. Brush tools
        self.brushButton.mousePressEvent = self.openBrushDialog

        # 4. main Image Viewer
        self.mainImageViewer.mousePressEvent = self.mousePressEvent
        self.mainImageViewer.mouseMoveEvent = self.mouseMoveEvent
        self.mainImageViewer.mouseReleaseEvent = self.mouseReleaseEvent

        # 5. listWidget
        self.listWidget.itemClicked.connect(self.getListWidgetIndex)

        # 6. label opacity
        self.lableOpacitySlider.valueChanged.connect(self.showHorizontalSliderValue)



    ######################## 
    ### Image Processing ###
    ########################

    def updateLabelandColormap(self, x, y):

        x, y = self.applyBrushSize(x, y)

        try : 
            self.label[y, x] = self.label_class 
            self.colormap[y, x] = self.img[y, x] * self.alpha + self.label_palette[self.label_class] * (1-self.alpha)
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        except BaseException as e : 
            print(e)

    ########################### 
    ### Mouse Event Handler ###
    ###########################

    def openBrushDialog(self, event):

        if hasattr(self, 'brushMenu'):
            self.brushMenu.close()
  
        self.use_brush = True
        self.brushMenu = BrushMenu()
        self.initBrushTools()
        
        self.brushMenu.move(event.globalX(), event.globalY())

        self.brushMenu.exec_()

    def initBrushTools(self):
        self.brushMenu.horizontalSlider.valueChanged.connect(self.setBrushSize)
        self.brushMenu.circleButton.clicked.connect(self.setBrushCircle)
        self.brushMenu.squareButton.clicked.connect(self.setBrushSquare)

    def setBrushCircle(self):
        self.circle = True

    def setBrushSquare(self):
        self.circle = False


    def openNewProjectDialog(self, event):
        
        self.newProjectDialog = newProjectDialog()
        self.newProjectDialog.nextButton.clicked.connect(self.openCategoryInfoDialog)

        self.newProjectDialog.exec()


    def openCategoryInfoDialog(self, event):

        self.newProjectDialog.close()

        self.setCategoryDialog = setCategoryDialog()
        self.setCategoryDialog.exec_()


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
        

    def showRoiMenu(self):
        self.roiAutoLabelButton.showMenu()
        
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
        pass

    #     x, y = getScaledPoint(event, self.scale)

    #     self.rect_end = x, y

    #     result = inference_segmentor(self.model, self.img[self.rect_start[1]: y, self.rect_start[0]: x, :])

    #     idx = np.argwhere(result[0] == 1)
    #     y_idx, x_idx = idx[:, 0], idx[:, 1]
    #     x_idx = x_idx + self.rect_start[0]
    #     y_idx = y_idx + self.rect_start[1]

    #     self.label[y_idx, x_idx] = 1
        
    #     self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
    #     self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
    #     self.resize_image()
        

    def setVerticalScale(self, new_scale):
        self.ver_scale = new_scale

    def setHorizontalScale(self, new_scale):
        self.hzn_scale = new_scale

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


