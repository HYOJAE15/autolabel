import sys

import cv2

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


from utils import resource_path, cvtArrayToQImage, blendImageWithColorMap





# Select folder "autolabel"
# MainWindow UI
# 경로 설정 시 현재 파일 위치가 어떻게 되나?(현재 디렉토리?, 현재 폴더 ?)
project_ui = '../ui_design/mainWindow.ui'

form = resource_path(project_ui)
form_class_main = uic.loadUiType(form)[0]

# Mainwindow class

class MainWindow(QMainWindow, form_class_main) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #### Attributes #### 
       

        # Brush
        
        self.drawing = False
        self.brushSize = 28
        self.brushColor = Qt.red
        self.lastPoint = QPoint()
        self.ver_scale = 1
        self.hzn_scale = 1

        # label opacity
        self.lableOpacitySlider.valueChanged.connect(self.showHorizontalSliderValue)

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
        #self.mainImageViewer.mouseMoveEvent = self.getPos
        #self.mainImageViewer.setMouseTracking = self.getmovingpos

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


        # QPixmap을 mainImageViewer 로 설정 및 resize 된 mainImageViewer 로 설정
        self.image = QPixmap(self.mainImageViewer.size())
        self.image.fill(Qt.transparent)
        print(f"self.mainImageViewer.size() {self.mainImageViewer.size()}")
        print(f"self.image.size() {self.image.size()}")


     # method for checking mouse clicks
    def getPos(self, event):

        print('event.pos', event.pos())



    def setVerticalScale(self, new_scale):
        self.ver_scale = new_scale


    def setHorizontalScale(self, new_scale):
        self.hzn_scale = new_scale

    def mousePressEvent(self, event):
        #print("mouse press", event.pos())
        if event.button() == Qt.LeftButton:
            self.drawing = True
            scaled_event_pos = QPoint(event.pos().x()*self.hzn_scale, event.pos().y()*self.ver_scale)
            print(f"click {scaled_event_pos}")
            self.lastPoint = scaled_event_pos
    
    def mouseMoveEvent(self, event):
        print("mouse move")
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            
            painter = QtGui.QPainter(self)
            painter.drawPixmap(self.rect(), self.image, self.image.rect())
            
            painter.setPen(QPen(self.brushColor, self.brushSize,
							Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            
            

            scaled_event_pos = QPoint(event.pos().x()*self.hzn_scale, event.pos().y()*self.ver_scale)
            
            print(f"move {scaled_event_pos}")
            painter.drawLine(self.lastPoint, scaled_event_pos)

            painter.end()
            self.mainImageViewer.setPixmap(QtGui.QPixmap(self.image))
            
            # self.mainImageViewer.setPixmap(self.image)
            self.lastPoint = scaled_event_pos

            

            self.update()

    def mouseReleaseEvent(self, event):
        print("mouse release")
        if event.button() == Qt.LeftButton:
            self.drawing = False
         
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
        # self.mainImageViewer.resize(scaled_pixmap.width(), scaled_pixmap.height())


    def showHorizontalSliderValue(self):

        if abs(self.alpha-(self.lableOpacitySlider.value() / 100)) > 0.03 :

            self.alpha = self.lableOpacitySlider.value() / 100

            self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
            
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))

            self.resize_image()    


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainWindow() 
    myWindow.show()
    app.exec_()
