import sys
import cv2
import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
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


sys.path.append("./dnn/mmseg")
from mmseg.apis import init_segmentor, inference_segmentor


# Select folder "autolabel"
# MainWindow UI
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
        self.set_roi_256 = False
        self.circle = True

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


        # 1. Menu
        self.treeView.clicked.connect(self.treeViewImage)
        self.actionOpenFolder.triggered.connect(self.actionOpenFolderFunction)

        # 2. zoom in and out
        self.ControlKey = False
        self.scale = 1
        self.zoomInButton.clicked.connect(self.on_zoom_in)
        self.zoomOutButton.clicked.connect(self.on_zoom_out)

        # 3. brush tools
        self.brushButton.clicked.connect(self.openBrushDialog)

        # 4. main Image Viewer
        self.mainImageViewer.mousePressEvent = self.mousePressEvent
        self.mainImageViewer.mouseMoveEvent = self.mouseMoveEvent
        self.mainImageViewer.mouseReleaseEvent = self.mouseReleaseEvent

        # 5. listWidget
        self.listWidget.itemClicked.connect(self.getListWidgetIndex)

        # 6. label opacity
        self.lableOpacitySlider.valueChanged.connect(self.showHorizontalSliderValue)

        # 7. auto label tools 
        self.roiMenu = QMenu()
        self.roiMenu.addAction("256*256", self.roi256)
        self.roiMenu.addAction("Set Rectangle", self.roiRec)
        self.roiAutoLabelButton.setMenu(self.roiMenu)
        self.roiAutoLabelButton.clicked.connect(self.showRoiMenu)
        #self.roiAutoLabelButton.clicked.connect(self.runRoiAutoLabel)
    
        # 8. handMoveTool
        self.hKey = False
        self.icon = QPixmap("./Icon/square.png")
        self.scaled_icon = self.icon.scaled(QSize(5, 5), Qt.KeepAspectRatio)
        self.custom_cursor = QCursor(self.scaled_icon)




    #### Methods ##### 


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
        

        # 이게 왜 안되지?? 
        # self.brushMenu.move(event.globalX(), event.globalY())

        self.brushMenu.show()

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
        self.newProjectDialog.folderButton.clicked.connect(self.setFolderPath)

        self.newProjectDialog.exec_()

    def setFolderPath(self):
        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder", "./")
        self.newProjectDialog.folderPath.setMarkdown(readFolderPath)

    def openCategoryInfoDialog(self, event):

        self.newProjectDialog.close()

        self.setCategoryDialog = setCategoryDialog()
        self.setCategoryDialog.exec_()

    def mousePressEvent(self, event):

        if self.use_brush : 
            self.brushPressOrReleasePoint(event)

        elif self.set_roi : 
            self.roiPressPoint(event)

        elif self.set_roi_256 :
            self.roi256PressPoint(event)


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


    








    
    

    


   

    


       
    

        
    
        

    def setVerticalScale(self, new_scale):
        self.ver_scale = new_scale

    def setHorizontalScale(self, new_scale):
        self.hzn_scale = new_scale

    


    def keyPressEvent(self, event):

            # zoom
        if event.key() == Qt.Key_Control:
            self.ControlKey = True
            QApplication.setOverrideCursor(self.custom_cursor)
            print(self.ControlKey)

            # handMove
        elif event.key() == Qt.Key_H:
            self.hKey = True
            QApplication.setOverrideCursor(self.custom_cursor)
            print(self.hKey)
          
         

    def keyReleaseEvent(self, event):

            # zoom
        if event.key() == Qt.Key_Control:
            self.ControlKey = False
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            print(self.ControlKey)

            # handMove
        elif event.key() == Qt.Key_H:
            self.hKey = False
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            print(self.hKey)
           
        # 줌 땡겨지는 위치를 조절 하자 
    def wheelEvent(self, event):
       
        if self.ControlKey:
            # mouse angleDelta 가 올리면 1, 내리면 -1 인대 줌인 줌 아웃을 어찌
            print(f"angleDelta{event.angleDelta().y()/120}")
            print(type(event.angleDelta().y()))
            self.mouseWheelAngleDelta = event.angleDelta().y()/120 # ->1
            
            if self.mouseWheelAngleDelta > 0 :
                print("된다!")
                print(self.mouseWheelAngleDelta+0.1)
                self.scale *= (self.mouseWheelAngleDelta+0.1)
                self.resize_image()

            elif self.mouseWheelAngleDelta < 0 :
                self.scale /= (abs(self.mouseWheelAngleDelta)+0.1)
                self.resize_image()
        
            #self.scale += event.angleDelta().y()/120  
            #self.resize_image()
            #print(f"self.scale {self.scale}")
            #print(event.angleDelta()/1200)
            #self.scale /= (1.0 + (event.angleDelta() / 1200)) # mouse wheel angleDelta Default = 120
            #self.resize_image()
            
            

            


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
    sys.exit(app.exec_())
