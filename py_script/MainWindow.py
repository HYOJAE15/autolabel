import os
import sys

import cv2

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils import resource_path
from Canvasmodule import Canvas



# Select folder "autolabel"
# MainWindow UI
ui_folder = 'ui_design'
project_folder_ui = 'mainWindow.ui'

form = os.path.join(ui_folder, project_folder_ui)
form_class_main = uic.loadUiType(form)[0]


# Mainwindow class

class MainWindow(QMainWindow, form_class_main) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # Image Blending
        self.alpha = 0.8

        # treeview
        self.folderPath = None
        self.pathRoot = QtCore.QDir.rootPath()
        self.treeModel = QFileSystemModel(self)
        self.dialog = QFileDialog()
        self.treeView.clicked.connect(self.treeViewImage)


        # label opacity horizontalslider
        self.win_name = "Label Opacity"
        self.slide_name = "Opacity"
    
        # file 메뉴 
        self.actionOpenImage.triggered.connect(self.actionOpenImageFunction)
        self.actionOpenFolder.triggered.connect(self.actionOpenFolderFunction)

        # zoom in and out
        self.scale = 1
        self.alpha = 1
        self.zoomInButton.clicked.connect(self.on_zoom_in)
        self.zoomOutButton.clicked.connect(self.on_zoom_out)

        # Brush 사용이 가능하도록 scrollArea 에 canvas 클래스 설정
        # brush 사용이 가능한 scrollArea 에 이미지를 불러 사용한다.
        self.canvas = Canvas()
        self.scrollArea.setWidget(self.canvas)

    # 메뉴바의 openimage 클릭시 mainimageviewer 에 이미지를 보여준다
    def actionOpenImageFunction(self) :
        """To be depreciated.
        """
        filename = QFileDialog.getOpenFileName(self, 'open image', 'C:/', 'images (*.jpg *.psd *.png)')
        print(f'filename', filename)
        imagepath = filename[0]
        print(f'imagepath', imagepath)
        cv_img1 = cv2.imread(imagepath)
        print(f'cv_img1', cv_img1)

        self.canvas.readImageFromFile(imagepath)
        
    # 메뉴바 의 openfolder 클릭시 treeview 에 해당 폴더를 보여준다, treeview function
    def actionOpenFolderFunction(self) :
        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder")
        self.folderPath = readFolderPath
        self.treeModel.setRootPath(self.folderPath)
        self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
        
        self.treeView.setModel(self.treeModel)
        self.treeView.setRootIndex(self.indexRoot)

    # treeview 에서 파일 클릭 시 클릭된 파일 로드 
    # 이미지 파일 클릭시 묶여있는 라벨링 이미지 와 함께 불러와 합성후 하나의 파일로 만들어 보여준다
    # @pyqtSlot(QModelIndex)
    def treeViewImage(self, index) :

        indexItem = self.treeModel.index(index.row(), 0, index.parent())
        imgPath = self.treeModel.filePath(indexItem)
        #cv_img1 = cv2.imread(filePath)
        # open cv image blending 시 필요한 이미지 2장을 어떻게 엮나?? original 과 페어링 된 colored 이미지 불러오기
        #cv_img2 = cv2.imread("./py_script/img_test_01.png")
        # print(f'indexitem', indexItem)  # treeview 에서 파일 클릭시 파일의 인덱스(?)를 저장 한다
        # print(f'imgPath', imgPath)  # 클릭한 파일의 인덱스 로 부터 해당 파일의 주소를 저장 한다.(해당 파일 주소 : 문자열)
       
        self.img = cv2.imread(imgPath) # 이미지 주소 내부 에 "사진" 을 인식하지 못한다, desktop 에서 test 실행
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB) # 이미지 주소 내부 에 "사진" 을 인식하지 못한다, desktop 에서 test 실행

        labelPath = imgPath.replace('/leftImg8bit/', '/gtFine/')
        labelPath = labelPath.replace( '_leftImg8bit.png', '_gtFine_labelIds.png')

        self.label = cv2.imread(labelPath, cv2.IMREAD_UNCHANGED) 

        self.color_label = np.zeros_like(self.img)

        

        # background, crack, rebar exposure, spalling, efflorescence(?)  
                         #  Back       crack         rebar ex       spalling     efflorescence 
        pallete = np.array([[0, 0, 0], [255, 0, 0], [255, 255, 0], [0, 0, 255], [255, 0, 255]])

        for idx, color in enumerate(pallete) : 
            self.color_label[self.label == idx, :] = self.img[self.label == idx, :] * alpha + color * (1-alpha)

        
        self.canvas.readImageFromArray(self.color_label)

        # 이미지를 띄울 캔버스 에 맞게 스케일 조절
        self.ver_scale = self.canvas.image.height() / self.scrollArea.height()
        self.hzn_scale = self.canvas.image.width() / self.scrollArea.width()

        self.canvas.setVerticalScale(self.ver_scale)
        self.canvas.setHorizontalScale(self.hzn_scale)
        

    # canvas 클래스로 설정된 scrollarea 에 띄워진 이미지를 줌 하는 기능 구현 
    def on_zoom_in(self, event):
        self.scale *= 2
        self.resize_image()

    def on_zoom_out(self, event):
        self.scale /= 2
        self.resize_image()

    def resize_image(self):
        
        size = self.qimage.size()
        scaled_pixmap = self.qimage.scaled(self.scale * size)
        self.mainImageViewer.setPixmap(QPixmap.fromImage(scaled_pixmap))


    # 투명도 조절 함수 
    # def change_opacity 
        # op_change_image = TWE$R^#$@%^
        # self.mainImageViewer.setPixmap(op_change_image)

    def onChange(self, x):
        alpha = x/100
        dst = cv2.addWeighted(self.cv_img1, 1-alpha, self.cv_img2, alpha, 0) 
        cv2.imshow(self.win_name, dst)




if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainWindow() 
    myWindow.show()
    app.exec_()
