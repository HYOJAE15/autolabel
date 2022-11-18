#!/usr/bin/python3
import os, sys

import cv2

import json


import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from scipy import ndimage

from utils.utils import *


from components.actions.actionFile import ActionFile

from components.buttons.autoLabelButton import AutoLabelButton
from components.buttons.brushButton import BrushButton
from components.buttons.eraseButton import EraseButton
from components.buttons.zoomButton import ZoomButton

from components.dialogs.brushMenuDialog import BrushMenu
from components.dialogs.eraseMenuDialog import EraseMenu
from components.dialogs.newProjectDialog import newProjectDialog
from components.dialogs.setCategoryDialog import setCategoryDialog

from components.opener.dialogOpener import dialogOpener

from components.widgets.treeView import TreeView

from components.model.concreteDamage import DnnModel
from ui_design.__import__ import ui_path


import time

# Select folder "autolabel"
# MainWindow UI
project_ui = 'mainWindow.ui'

form = ui_path(project_ui)
form_class_main = uic.loadUiType(form)[0]

# Mainwindow class

class MainWindow(QMainWindow, form_class_main,
                 AutoLabelButton, BrushButton, EraseButton,
                 dialogOpener, 
                 ActionFile, TreeView) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # from ** import ** 

        # Default Model
        # # FIXME fix hard coding ... 
        # config_file = './dnn/checkpoints/2022.01.06 cgnet general crack 2048/cgnet_2048x2048_60k_CrackAsCityscapes.py'
        # checkpoint_file = './dnn/checkpoints/2022.01.06 cgnet general crack 2048/iter_60000.pth'
        # self.model = init_segmentor(config_file, 
        #                             checkpoint_file, 
        #                             device='cuda:0')


        """Attributes
            brushSize (int): size of brush 
            eraseSize (int): size of eraser 
            ver_scale (float): vertical scale to plot image 
            hzn_scale (float): horizontal scale to plot image
            x, y (int): cordinate of (????, FIXME) 
            label_class (int): currently working class number, used to call working layer 
            label_segmentation (int): what is this?? FIXME
            alpha (float): blend ratio between colormap and original image 
            use_brush (bool): True when using brush
            use_erase (bool): True when using eraser 
            set_roi (bool): if True, an user defines roi size for each auto-labeling
            set_roi_256 (bool): if True, auto label use roi of 256x256
            circle (bool): if True, brush or eraser shape is circle, else rectangle 
        """
        
        self.brushSize = 2
        self.eraseSize = 2
        self.ver_scale = 1.
        self.hzn_scale = 1.
        self.x = 0 
        self.y = 0 
        self.label_class = 0
        self.label_segmentation = 1
        self.alpha = 0.5
        self.use_brush = False
        self.use_erase = False
        self.set_roi = False
        self.set_roi_256 = False
        self.circle = True
        
        
        # treeview setting 
        self.openFolderPath = None
        self.imgPath = None
        self.folderPath = None
        self.pathRoot = QtCore.QDir.rootPath()
        self.treeModel = QFileSystemModel(self)
        self.dialog = QFileDialog()   # Find the Folder or File Dialog
        self.treeView.clicked.connect(self.treeViewImage)
        self.treeView.clicked.connect(self.askSave)
        
        # 1. Menu
        self.actionOpenFolder.triggered.connect(self.actionOpenFolderFunction)
        self.actionAddNewImages.triggered.connect(self.addNewImages)
        self.actionNewProject.triggered.connect(self.createNewProjectDialog)
        self.actionOpenProject.triggered.connect(self.openExistingProject)

        # 2. Zoom in and out
        self.ControlKey = False
        self.scale = 1
        
        # 3. brush & erase tools
        self.brushButton.clicked.connect(self.openBrushDialog)
        self.eraseButton.clicked.connect(self.openEraseDialog)

        # 4. main Image Viewer
        self.mainImageViewer.mousePressEvent = self.mousePressEvent
        self.mainImageViewer.mouseMoveEvent = self.mouseMoveEvent
        self.mainImageViewer.mouseReleaseEvent = self.mouseReleaseEvent
        self.mainImageViewer.wheelEvent = self.storeXY

        self.scrollArea.wheelEvent = self.wheelEventScroll


        # 5. listWidget
        self.listWidget.itemClicked.connect(self.getListWidgetIndex)
        # self.listWidget.itemDoubleClicked.connect(self.getListWidgetCheckState)
        self.listWidget.itemChanged.connect(self.LayerOnOff)
        
        # 6. label opacity
        self.lableOpacitySlider.valueChanged.connect(self.showHorizontalSliderValue)
        self.labelOpacityCheckBox.stateChanged.connect(self.labelOpacityOnOff)

        # 7. auto label tools 
        self.roiMenu = QMenu()
        self.roiMenu.addAction("256*256", self.roi256)
        self.roiMenu.addAction("Set Rectangle", self.roiRec)
        self.roiMenu.addAction("Full image", self.roiFull)
        self.roiAutoLabelButton.setMenu(self.roiMenu)
        self.roiAutoLabelButton.clicked.connect(self.showRoiMenu)
        #self.roiAutoLabelButton.clicked.connect(self.runRoiAutoLabel)
    
        # 8. handMoveTool
        self.hKey = False
        self.icon = QPixmap("./Icon/square.png")
        self.scaled_icon = self.icon.scaled(QSize(5, 5), Qt.KeepAspectRatio)
        self.custom_cursor = QCursor(self.scaled_icon)



            

    #### Methods ##### 
    
    def storeXY(self, event):
        """I don't know What this is for FIXME
        """
        if self.ControlKey:
            self.img_v_x = event.pos().x()
            self.img_v_y = event.pos().y()
    

    ######################## 
    ### Image Processing ###
    ########################


    def addNewImages(self):
        """Add images to working directory 
            FIXME: This function is so slow now... need to improve import speed. 
        Args : 

        """
        
        try : # FIXME: Remove this try, except if possible  

            if self.openFolderPath :
                self.imgPath = self.openFolderPath
                print(self.openFolderPath)
                print(self.imgPath)

            else :
                print(f'dang {self.imgPath}')
                # self.imgPath = self.openFolderPath
                # print(f"cityscapedataset 비준수 {self.openFolderPath}")

            readFilePath = self.dialog.getOpenFileNames(
                caption="Add images to current working directory", filter="Images (*.png *.jpg *.tiff)"
                )
            images = readFilePath[0]


                # check if images are from same folder
            if self.treeModel.rootPath() in os.path.dirname(images[0]):
                print("same foler")
                return None

            if self.imgPath :

                dotSplit_imgPath = self.imgPath.split(".")
                slashSplit_imgPath = self.imgPath.split("/")
              
                    # clicked img_file
                if 'png' in dotSplit_imgPath and 'leftImg8bit' in slashSplit_imgPath :

                    img_save_folder = os.path.dirname(self.imgPath)
                   
                    img_label_folder = os.path.dirname(self.labelPath)

                    print("png, left")
                
                    # clicked img_folder
                elif 'png' not in dotSplit_imgPath and 'leftImg8bit' in slashSplit_imgPath :
    
                    img_save_folder = self.imgPath
                    img_save_folder = img_save_folder.replace( '_leftImg8bit.png', '')  
                
                    img_label_folder = img_save_folder.replace('/leftImg8bit/', '/gtFine/')
                    img_label_folder = img_label_folder.replace( '_leftImg8bit.png', '')
                    print('left')

                else :   # 선택된 폴더가 시티스케이프 데이터셋 이 아닌 다른 경우 에러 발생 UnboundLocalError
                    print('not cityscapeDataset')
    
                for img in images:
                
                    temp_img = cv2.imdecode(np.fromfile(img, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                    img_filename = os.path.basename(img) # -> basename is file name
                    img_filename = img_filename.replace(' ', '')
                    img_filename = img_filename.replace('.jpg', '.png')
                    img_filename = img_filename.replace('.JPG', '.png')
                    img_filename = img_filename.replace('.tiff', '.png')
                    img_filename = img_filename.replace('.png', '_leftImg8bit.png')

                    img_gt_filename = img_filename.replace( '_leftImg8bit.png', '_gtFine_labelIds.png')
                    gt = np.zeros((temp_img.shape[0], temp_img.shape[1]), dtype=np.uint8)

                    is_success, org_img = cv2.imencode(".png", temp_img)
                    org_img.tofile(os.path.join(img_save_folder, img_filename))

                    is_success, gt_img = cv2.imencode(".png", gt)
                    gt_img.tofile(os.path.join(img_label_folder, img_gt_filename))

                    # check file extension -> change extension to png 
                    # create corresponding label file 

                    print(f'7 {os.path.join(img_save_folder, img_filename)}')

            else :
                print("self.imgPath is None")
        
        except IndexError as e :
            print(e)

        except UnboundLocalError as e :
            print(e)


    def layerViewMode(self):
        """
            FIXME: What this is for?? 
        """
        pass

    def updateLayers(self, x, y):
        """Update layers 
            
            self.layers
            self.label_class 
            x, y (int): coordinates to convert label 
        """
        attrs = ['layers', 'label_class']
        for attr in attrs: 
            assert hasattr(self, attr)
        
        try : # FIXME: Why do we need this try, exception 
            # print(f"label_class {self.label_class}")
            if self.use_brush :
                self.layers[self.label_class][y, x] = 1

            elif self.use_erase :
                self.layers[self.label_class][y, x] = 0
            
        except BaseException as e : 
            print(e)
        

    def updateLabelFromLayers(self, x, y):
        """Update label from each label 

            Args 
                self.label
                self.layers 
                x, y (int): coordinates to convert label
        
        """
        attrs = ['label', 'layers']
        for attr in attrs: 
            assert hasattr(self, attr)

        self.label[y, x] = 0
        temp_label = self.label[y, x]

        for idx in reversed(range(1, len(self.layers))):             
            temp_label = np.where(self.layers[idx][y, x], idx, temp_label)

        self.label[y, x] = temp_label

        
    def updateColormapFromLabel(self, x, y):
        try :             
            self.colormap[y, x] = self.img[y, x] * self.alpha + self.label_palette[self.label[y, x]] * (1-self.alpha)

            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        except BaseException as e : 
            print(e)
        

    def updateLabelandColormap(self, x, y):
        
        if self.use_brush :
            x, y = self.applyBrushSize(x, y)
        elif self.use_erase :
            x, y = self.applyEraseSize(x, y)


        try : 
            # print(f"label_class {self.label_class}")
            # print(type(self.label_class))
            
            if self.use_brush :
                self.label[y, x] = self.label_class
                self.colormap[y, x] = self.img[y, x] * self.alpha + self.label_palette[self.label_class] * (1-self.alpha)

            elif self.use_erase :
                self.label[y, x] = 0
                print("eraseMode")
                self.colormap[y, x] = self.img[y, x] * self.alpha + self.label_palette[0] * (1-self.alpha)

            
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        except BaseException as e : 
            print(e)

    


    def openExistingProject(self):

        try :

            readFilePath = self.dialog.getOpenFileName(
                caption="Select Project File", filter="*.hdr"
                )
            hdr_path = readFilePath[0]
            
            folderPath = os.path.dirname(hdr_path)
            print(folderPath)
            cityscapeDataset_folderPath = os.path.join(folderPath, "leftImg8bit")
                # openFolderPath 를 None 으로 받고 treeView 에서 선택한 파일 또는 폴더 주소를 받는다.
            self.openFolderPath = None
            print(os.path.join(folderPath, "leftImg8bit"))
            self.fileNameLabel.setText(cityscapeDataset_folderPath)
            self.treeModel.setRootPath(os.path.join(folderPath, 'leftImg8bit'))
            self.indexRoot = self.treeModel.index(self.treeModel.rootPath())
            self.treeView.setModel(self.treeModel)
            self.treeView.setRootIndex(self.indexRoot)
            

            with open(hdr_path) as f:
                hdr = json.load(f)

            self.listWidget.clear()

            self.label_palette = []

            for idx, cat in enumerate(hdr['categories']):
                name, color = cat[0], cat[1]
                color = json.loads(color)
                self.listWidget.addItem(name)
                iconPixmap = QPixmap(20, 20)
                iconPixmap.fill(QColor(color[0], color[1], color[2]))
                self.listWidget.item(idx).setIcon(QIcon(iconPixmap))
                self.label_palette.append(color)
                print(f"idx{idx}")
                self.listWidget.item(idx).setCheckState(Qt.Checked)
                # self.listWidgetCheckBox = QListWidgetItem()
                # self.listWidgetCheckBox.setCheckState(Qt.Checked)
                # self.listWidget.addItem(self.listWidgetCheckBox)

            self.label_palette = np.array(self.label_palette)
            print(f"label_palette : {self.label_palette}")
            print(f"palette type : {type(self.label_palette)}")

        except FileNotFoundError as e:
            print(e)


    def createNewProjectDialog(self, event):
            # new_project_info 를 딕셔너리 자료형으로 설정 한다.
        self.new_project_info = {}

        self.newProjectDialog = newProjectDialog()
            # textProjectName : QTextEdit
        self.newProjectDialog.textProjectName.textChanged.connect(self.setProjectName)
        self.newProjectDialog.nextButton.clicked.connect(self.openCategoryInfoDialog)
        self.newProjectDialog.folderButton.clicked.connect(self.setFolderPath)

        self.newProjectDialog.exec()
        

    def setProjectName(self):
            # 딕셔너리 자료형으로 설정한 변수 에서 key 를 설정해주고 해당 key 에 value 값을 할당 한다.
            # self.new_project_info = {'project_name': self.newProjectDialog.textProjectName.toPlainText() }
        self.new_project_info['project_name'] = self.newProjectDialog.textProjectName.toPlainText()
        print(self.new_project_info['project_name'])


    def setFolderPath(self):

        readFolderPath = self.dialog.getExistingDirectory(None, "Select Folder", "./")
        print(readFolderPath)
            # folderPath : QTextEdit
        self.newProjectDialog.folderPath.setMarkdown(readFolderPath)
        self.new_project_info['folder_path'] = readFolderPath
        print(self.new_project_info)


    def createProjectHeader(self):

        createProjectFile_name = self.new_project_info['project_name'] + ".hdr"
        print(createProjectFile_name)

        path = self.new_project_info['folder_path']
        n_row = self.setCategoryDialog.tableWidget.rowCount()

        self.new_project_info['categories'] = []

        for i in range(n_row):
            self.new_project_info['categories'].append(
                [
                    self.setCategoryDialog.tableWidget.item(i, 0).text(),
                    self.setCategoryDialog.tableWidget.item(i, 2).text()
                ]
                )
            
        with open(os.path.join(path, createProjectFile_name), 'w') as fp:
            json.dump(self.new_project_info, fp)
            self.setCategoryDialog.close()


    def mousePressEvent(self, event):
        # print("mousePressEvent")

        if self.hKey : 
            self.scrollAreaMousePress(event)

        elif self.use_brush : 
            self.brushPressOrReleasePoint(event)

        elif self.use_erase :
            self.erasePressOrReleasePoint(event)

        elif self.set_roi : 
            self.roiPressPoint(event)

        elif self.set_roi_256 :
            self.roi256PressPoint(event)


    def mouseMoveEvent(self, event):

        if self.hKey : 
            self.scrollAreaMouseMove(event)

        elif self.use_brush : 
            self.brushMovingPoint(event)

        elif self.use_erase :
            self.eraseMovingPoint(event)

        elif self.set_roi : 
            self.roiMovingPoint(event)

    def mouseReleaseEvent(self, event): 

        if self.hKey :
            pass

        elif self.use_brush : 
            self.brushPressOrReleasePoint(event)

        elif self.use_erase :
            self.erasePressOrReleasePoint(event)

        elif self.set_roi : 
            self.roiReleasePoint(event)
    
    def showRoiMenu(self):
        self.roiAutoLabelButton.showMenu()

    def setVerticalScale(self, new_scale):
        self.ver_scale = new_scale

    def setHorizontalScale(self, new_scale):
        self.hzn_scale = new_scale

         
    def keyPressEvent(self, event):
        print(event.key())
            
        if event.key() == Qt.Key_Control:
            self.ControlKey = True
            

        elif event.key() == Qt.Key_H: 
            self.hKey = True
            print(QCursor().shape())
            QApplication.setOverrideCursor(Qt.OpenHandCursor)

        elif event.key() == 65 : # A Key
            
            self.set_roi_256 = 1-self.set_roi_256

            if self.set_roi_256 : 
                self.roiAutoLabelButton.setChecked(True)

            else : 
                self.roiAutoLabelButton.setChecked(False)

            # S to A
            if self.set_roi :
                self.set_roi = 1-self.set_roi


            if self.use_erase : 
                self.use_erase = False
                self.eraseButton.setChecked(False)

            if  hasattr(self, 'eraseMenu'):   
                self.eraseMenu.close()

            if self.use_brush :
                self.use_brush = False
                self.brushButton.setChecked(False)
                
            if hasattr(self, 'brushMenu'):
                self.brushMenu.close()

            # if self.ControlKey :
            #     self.roiFull()

        elif event.key() == 83 : # S key 

            # Save File 
            if self.ControlKey : 
                print('Save')
                imwrite(self.labelPath, self.label)
                self.saveImgName = os.path.basename(self.imgPath)
                # print(self.saveImgName)
                self.situationLabel.setText(self.saveImgName + "을(를) 저장하였습니다.")
            
            # shortcut key: set_roi set Rectangle  
            elif self.ControlKey == False :
                print("autoLabel_setRectangle")
                self.set_roi = 1-self.set_roi

                if self.set_roi : 
                    self.roiAutoLabelButton.setChecked(True)

                else : 
                    self.roiAutoLabelButton.setChecked(False)

                # A to S
                if self.set_roi_256 :       
                    self.set_roi_256 = 1-self.set_roi_256


                if self.use_erase : 
                    self.use_erase = False
                    self.eraseButton.setChecked(False)

                if  hasattr(self, 'eraseMenu'):   
                    self.eraseMenu.close()

                if self.use_brush :
                    self.use_brush = False
                    self.brushButton.setChecked(False)
                    
                if hasattr(self, 'brushMenu'):
                    self.brushMenu.close()

            
    
        elif event.key() == 66 : # B Key
            print("B")

            if self.use_brush == True :
                self.use_brush = False
                self.brushButton.setChecked(False)

                if hasattr(self, 'brushMenu'):
                    self.brushMenu.close()  

            else :
                self.openBrushDialog(event)
                
            if self.use_erase : 
                self.use_erase = False
                self.eraseButton.setChecked(False)
                
            if  hasattr(self, 'eraseMenu'):   
                self.eraseMenu.close()
                
            if self.set_roi_256:
                self.set_roi_256 = False
                self.roiAutoLabelButton.setChecked(False)

            if self.set_roi:
                self.set_roi = False
                
        elif event.key() == 69 : # E Key
            print("E")

            if self.use_erase == True :
                self.use_erase = False
                self.eraseButton.setChecked(False)

                if  hasattr(self, 'eraseMenu'):   
                    self.eraseMenu.close()

            else :
                self.openEraseDialog(event)

            if self.use_brush :
                self.use_brush = False
                self.brushButton.setChecked(False)

            if hasattr(self, 'brushMenu'):
                self.brushMenu.close()

            if self.set_roi_256:
                self.set_roi_256 = False
                self.roiAutoLabelButton.setChecked(False)

            if self.set_roi:
                self.set_roi = False

        elif event.key() == 70 : # f Key
            print("filling works")
            self.layers[self.label_class] = ndimage.binary_fill_holes(self.layers[self.label_class])

            for idx in reversed(range(1, len(self.layers))): 
                self.label = np.where(self.layers[idx], idx, self.label) 

            self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
                
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))

            self.resize_image()
            

        elif event.key() == 81: # Q key
            self.labelOpacityCheckBox.setChecked(1-self.labelOpacityCheckBox.isChecked())
            self.labelOpacityOnOff()
            # Brush
            # B_key 한번 press 후 Brush 기능 키고 끄자 

        

        # Delete Image
        elif event.key() == 16777223 : # Delete key
            print(event.key())
            
            print(self.labelPath)
            print(self.imgPath)
            os.remove(self.imgPath)    
            os.remove(self.labelPath)
                
        else :
            print(event.key())
          
    def keyReleaseEvent(self, event):

            # zoom
        if event.key() == Qt.Key_Control:
            self.ControlKey = False
            # QApplication.restoreOverrideCursor()

            # handMove
        elif event.key() == Qt.Key_H:
            self.hKey = False
            QApplication.restoreOverrideCursor()
            
        
        
    def scrollAreaMousePress(self, event):

        self.hand_last_point = QPoint(QCursor.pos().x(), QCursor.pos().y())
        
    def scrollAreaMouseMove(self, event):


        delta_y = self.hand_last_point.y() - QCursor.pos().y()
        delta_x = self.hand_last_point.x() -  QCursor.pos().x() 

        setvalueY = self.scrollArea.verticalScrollBar().value()
        setvalueX = self.scrollArea.horizontalScrollBar().value()
        
        self.scrollArea.verticalScrollBar().setValue(setvalueY + delta_y)
        self.scrollArea.horizontalScrollBar().setValue(setvalueX + delta_x)

        self.hand_last_point = QPoint(QCursor.pos().x(), QCursor.pos().y())

    
    def wheelEventScroll(self, event):
        
        self.mouseWheelAngleDelta = event.angleDelta().y() # -> 1 (up), -1 (down)
        if self.ControlKey:
                
            if self.mouseWheelAngleDelta > 0: 
                self.scale *= 1.1
                width_tobe = self.mainImageViewer.geometry().width() * 1.1
                height_tobe = self.mainImageViewer.geometry().height() * 1.1
            else : 
                self.scale /= 1.1
                width_tobe = self.mainImageViewer.geometry().width() / 1.1
                height_tobe = self.mainImageViewer.geometry().height() / 1.1

            self.resize_image()

            _width_diff = width_tobe - self.scrollArea.geometry().width()
            _height_diff = height_tobe - self.scrollArea.geometry().height() 

            x_max_img_v = self.mainImageViewer.geometry().width()
            y_max_img_v = self.mainImageViewer.geometry().height()

            set_hor_max = _width_diff + 45 if _width_diff > 0 else 0
            set_ver_max = _height_diff + 45 if _height_diff > 0 else 0

            self.scrollArea.horizontalScrollBar().setRange(0, set_hor_max) 
            self.scrollArea.verticalScrollBar().setRange(0, set_ver_max) 
            
            ver_max = self.scrollArea.verticalScrollBar().maximum()
            hor_max = self.scrollArea.horizontalScrollBar().maximum()
            
            if self.scrollArea.verticalScrollBar().maximum() > 0: 
                setvalueY = self.img_v_y/y_max_img_v*ver_max                
                self.scrollArea.verticalScrollBar().setValue(setvalueY)

            if self.scrollArea.horizontalScrollBar().maximum() > 0: 
                setvalueX = self.img_v_x/x_max_img_v*hor_max
                
                self.scrollArea.horizontalScrollBar().setValue(setvalueX)

        else : 
            scroll_value = self.scrollArea.verticalScrollBar().value()
            self.scrollArea.verticalScrollBar().setValue(scroll_value - self.mouseWheelAngleDelta)

    def resize_image(self):
        size = self.pixmap.size()
        self.scaled_pixmap = self.pixmap.scaled(self.scale * size)
        self.mainImageViewer.setPixmap(self.scaled_pixmap)

    def showHorizontalSliderValue(self):

        self.labelOpacityCheckBox.setChecked(True)

        if abs(self.alpha-(self.lableOpacitySlider.value() / 100)) > 0.03 :
            self.alpha = self.lableOpacitySlider.value() / 100
            self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
            self.resize_image()    

    def labelOpacityOnOff(self):
        
        if self.labelOpacityCheckBox.isChecked():
            self.alpha = self.lableOpacitySlider.value() / 100
        else : 
            self.alpha = 1 
        
        self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
        self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        self.resize_image()    

    def getListWidgetIndex (self):

        print(f"self.listWidget.currentRow(){self.listWidget.currentRow()}")
        
        self.label_class = self.listWidget.currentRow()
        self.label_segmentation = self.listWidget.currentRow()

        if self.use_brush :
            print("Brush")
            # roi 설정이 되 있어야 모델 선택이 가능함
            
        elif self.set_roi or self.set_roi_256 :
            
            if self.label_segmentation == 1 :
                DnnModel.crackModel(self)

            elif self.label_segmentation == 2 :
                DnnModel.efflorescenceModel(self)

            elif self.label_segmentation == 3 :
                DnnModel.rebarExposureModel(self)
                
            elif self.label_segmentation == 4 :
                DnnModel.spallingModel(self)
            




        
        # listWidget 에서 class를 double click 시 checkBox 상태 변환과 layer on, off 
    def getListWidgetCheckState(self):
        print("Double Clicked!!")
        print(self.listWidget.item(self.label_class).checkState())
        self.listWidgetCheckState = self.listWidget.item(self.label_class).checkState()
        if self.listWidgetCheckState==2 : # checked

            self.listWidget.item(self.label_class).setCheckState(Qt.Unchecked)
            
            self.layer_palette = self.label_palette
            self.layer_palette_idx = self.layer_palette[self.label_class]
            print(f"idx : {self.layer_palette_idx}")
            self.layer_palette[self.label_class]=0
            print(f"layer_palette : {self.layer_palette}")
            print(f"label_palette : {self.label_palette}")

            print(f"idx : {self.layer_palette_idx}")
            

            self.layer_colormap = blendImageWithColorMap(self.img, self.label, self.layer_palette, self.alpha)
            self.pixmap = QPixmap(cvtArrayToQImage(self.layer_colormap))
            self.resize_image()    


        elif self.listWidgetCheckState==0 :
            
            self.listWidget.item(self.label_class).setCheckState(Qt.Checked)
            
            print(f"layer_palette : {self.layer_palette}")
            print(f"label_palette : {self.label_palette}")

            print(f"idx : {self.layer_palette_idx}")
            self.label_palette[self.label_class]=self.layer_palette_idx


            self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
            self.resize_image()    


        

    def LayerOnOff(self):
        print("Layer on&off")


        
        
if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = MainWindow() 
    myWindow.show()
    sys.exit(app.exec_())
