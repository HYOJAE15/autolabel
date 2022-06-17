import sys
import cv2

import json
import os


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
        self.imgPath = None
        self.folderPath = None
        self.pathRoot = QtCore.QDir.rootPath()
        self.treeModel = QFileSystemModel(self)
        self.dialog = QFileDialog()   # Find the Folder or File Dialog
        self.treeView.clicked.connect(self.treeViewImage)
        # self.treeView.keyPressEvent.connect(self.pressKey)
        
        # 1. Menu
        self.actionOpenFolder.triggered.connect(self.actionOpenFolderFunction)

        # 2. zoom in and out
        self.ControlKey = False
        self.actionAddNewImages.triggered.connect(self.addNewImages)
        self.actionNewProject.triggered.connect(self.createNewProjectDialog)
        self.actionOpenProject.triggered.connect(self.openExistingProject)
        # self.actionCreate_a_Project.triggered.connect(self.openCreateProjectDialog)

        # 2. Zoom in and out
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


        # addNewImage 버튼 클릭 후 아무 파일 도 선택 안할 시 에러 

    def addNewImages(self):
        readFilePath = self.dialog.getOpenFileNames(
            caption="Add images to current working directory", filter="Images (*.png *.jpg)"
            )
        images = readFilePath[0]
        print(f'1 {readFilePath}')
        print(f'2 {images}')

        print(f'3 {os.path.dirname(images[0])}')
        print(f'4 {self.treeModel.rootPath()}')

            # check if images are from same folder
        if self.treeModel.rootPath() in os.path.dirname(images[0]):
            print("same foler")
            return None

         
            #
        if self.imgPath :

            dotSplit_imgPath = self.imgPath.split(".")
            print(f"5 {dotSplit_imgPath}")

                # clicked img_file
            if 'png' in dotSplit_imgPath :

                img_save_folder = os.path.dirname(self.imgPath)
                print(img_save_folder)
                img_label_folder = os.path.dirname(self.labelPath)
                print(img_label_folder)

                # clicked img_folder
            elif 'png' not in dotSplit_imgPath :
 
                img_save_folder = self.imgPath
                img_save_folder = img_save_folder.replace( '_leftImg8bit.png', '')  
                print(img_save_folder)
            
                img_label_folder = img_save_folder.replace('/leftImg8bit/', '/gtFine/')
                img_label_folder = img_label_folder.replace( '_leftImg8bit.png', '')
            
                # img_label_folder = self.labelPath
                print(img_label_folder)

                #return img_save_folder, img_label_folder 
                # if loop is end when get return value 


                

        
            for img in images:
            
                # temp_img = cv2.imread(img, cv2.IMREAD_UNCHANGED) 
                temp_img = cv2.imdecode(np.fromfile(img, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

                # print(f"temp_img {temp_img}")
                # print(temp_img.shape)

                img_filename = os.path.basename(img) # -> basename is file name
                print(f"6 {img_filename}") # -> image name 
                img_filename = img_filename.replace(' ', '')
                img_filename = img_filename.replace('.jpg', '.png')
                img_filename = img_filename.replace('.png', '_leftImg8bit.png')

                img_gt_filename = img_filename.replace( '_leftImg8bit.png', '_gtFine_labelIds.png')
                gt = np.zeros((temp_img.shape[0], temp_img.shape[1]), dtype=np.uint8)

                cv2.imwrite(os.path.join(img_save_folder, img_filename), temp_img)
                cv2.imwrite(os.path.join(img_label_folder, img_gt_filename), gt)
                # check file extension -> change extension to png 
                # create corresponding label file 

                print(f'7 {os.path.join(img_save_folder, img_filename)}')

        else :
            print("self.imgPath is None")

        

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
         
        # 좌표를 받고 싶다면 mousePressEvent 활용
        #self.brushMenu.move(event.globalX(), event.globalY())

        self.brushMenu.show()

    def initBrushTools(self):
        self.brushMenu.horizontalSlider.valueChanged.connect(self.setBrushSize)
        self.brushMenu.circleButton.clicked.connect(self.setBrushCircle)
        self.brushMenu.squareButton.clicked.connect(self.setBrushSquare)

    def setBrushCircle(self):
        self.circle = True

    def setBrushSquare(self):
        self.circle = False

    

        
        # openProject 버튼 클릭 후 아무 파일 도 선택 안할시 에러 


    def openExistingProject(self):

        readFilePath = self.dialog.getOpenFileName(
            caption="Select Folder", filter="*.hdr"
            )
        hdr_path = readFilePath[0]
        
        folderPath = os.path.dirname(hdr_path)
        print(folderPath)
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

        self.label_palette = np.array(self.label_palette)


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


    def openCategoryInfoDialog(self, event):

        self.newProjectDialog.close()

        self.setCategoryDialog = setCategoryDialog()
        self.setCategoryDialog.createButton.clicked.connect(self.createProjectHeader)
        self.setCategoryDialog.exec()

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

            # Delete Image
        elif event.key() == 16777223 : # delete key
            print(event.key())
            
            print(self.labelPath)
            print(self.imgPath)
            os.remove(self.imgPath)    
            os.remove(self.labelPath)

            # Save Image
        elif event.key() == 83 : # S key
            if self.ControlKey : 
                cv2.imwrite(self.labelPath, self.label) 
                print('Save')

        else :
            print(event.key())
          
    def keyReleaseEvent(self, event):

            # zoom
        if event.key() == Qt.Key_Control:
            self.ControlKey = False
            QApplication.restoreOverrideCursor()
            print(self.ControlKey)

            # handMove
        elif event.key() == Qt.Key_H:
            self.hKey = False
            QApplication.restoreOverrideCursor()
            print(self.hKey)
           

    def wheelEvent(self, event):
       
        if self.ControlKey:

            self.mouseWheelAngleDelta = event.angleDelta().y()/120 # -> 1 (up), -1 (down)
            
            if self.mouseWheelAngleDelta > 0 :

                self.scale *= (self.mouseWheelAngleDelta+0.1)
                self.resize_image()

            elif self.mouseWheelAngleDelta < 0 :

                self.scale /= (abs(self.mouseWheelAngleDelta)+0.1)
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
    sys.exit(app.exec_())
