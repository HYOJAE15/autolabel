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

# Mainwindow class

class MainWindow(QMainWindow, form_class_main) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #### Attributes #### 


        # 메인에서 실행 했으니 메인 클래스의 인스턴스로 생성된 변수 들은 (self.변수) 매서드 내에서 재지정 되도 재지정 값을 저장
        # 타 모듈 에서 인스턴스로 생성된 변수들은 모듈을 부를때 마다 처음 지정한 인스턴스 변수로 지정 된다.
        # 타 모듈 에서 인스턴스로 생성된 변수들은 부를 때 마다 처음 값으로 리셋 된다. 
        # 모듈 부른다(인스턴스 변수 호출 및 각 매서드에서 지정 하면 변수 재지정), 다시부른다(다시 처음 지정값)
    
        self.brushSize = 1
        self.ver_scale = 1
        self.hzn_scale = 1
        self.x = 0 
        self.y = 0 
        self.label_class = 0
        self.alpha = 0.5
        self.use_brush = False
        self.set_roi = False
        self.set_roi_256 = False

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
        self.ControlKey = False
        self.scale = 1
        self.zoomInButton.clicked.connect(self.on_zoom_in)
        self.zoomOutButton.clicked.connect(self.on_zoom_out)

        # brush tools

        self.brushButton.clicked.connect(self.openBrushDialog)

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

    
    def openBrushDialog(self):
        self.brushMenu = BrushMenu()
        self.brushMenu.exec_()
        self.use_brush = self.brushMenu.use_brush
        self.brushSize = self.brushMenu.brushSize

        if self.use_brush:
            self.brushButton.setChecked(True)
            self.roiAutoLabelButton.setChecked(False)
            #self.brushMenu.horizontalSlider.setValue(self.brushSize)
            #self.brushMenu.lineEdit.setText(f'{self.brushSize} px')
            self.brushMenu.horizontalSlider.valueChanged.connect(self.setBrushSize)
        
        
        
        
    
    def setBrushSize(self):
        self.brushSize = self.brushMenu.brushSize

    def openBrushMenuDialog(self):
        # brushMenuDialog 모듈의 BrushDialog 클래스 에 대한 인스턴스를 생성 
        # BrushDialogClass's Instance
        # 클래스 에 대한 인스턴스로 받아들인 값을 사용한다
        BCI = BrushDialog()
        # exec_ 로 띄워진 화면은 닫기 전 까지는 parent 화면으로 넘어갈수 없다.
        BCI.exec_()
        
        self.BCIValue = BCI.BrushSize
        self.use_brush = BCI.use_brush
        print(f"before self.use_brush {self.use_brush}")
        # 인스턴스로 받아들인 값으로 활용해서 Brush Size 조절 
        

        # 창을 그냥 닫을 시 오류를 피하는 방법...  오류 피할려면 모두 loop 돌려야 ??
        if self.BCIValue:
            self.brushButton.setChecked(True)
            print(f"self.BCIValue = {self.BCIValue}")
            print(f"after self.use_brush {self.use_brush}")

        else :
            self.brushButton.setChecked(False)
            print("Brush Size 를 선택하지 않았습니다.")        

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


        # 256*256 크기의 구간 설정 상자를 만든다, 
    def roi256(self):
        print("roi256")
        self.brushButton.setChecked(False)
        self.roiAutoLabelButton.setChecked(True)

        self.use_brush = False

        self.set_roi = False

        self.set_roi_256 = True


    def roiRec(self):
        self.brushButton.setChecked(False)
        self.roiAutoLabelButton.setChecked(True)
        print(f"self.use_brush {self.use_brush}")

        self.use_brush = False

        self.set_roi = True
        
        self.set_roi_256 = False

        print(f"self.set_roi {self.set_roi}")
        print(f"self.use_brush {self.use_brush}")

        # 클릭 점을 중앙점 으로 256*256 사이즈 상자 나오게 
    def roi256PressPoint(self, event):

        x, y = getScaledPoint(event, self.scale)

        #self.rect_center = x, y

        self.rect_start = x-128, y-128

        self.rect_end = x+128, y+128

        thickness = 2

            
        rect_hover = cv2.rectangle(
            self.colormap.copy(), self.rect_start, self.rect_end, (255, 255, 255), thickness)

        self.pixmap = QPixmap(cvtArrayToQImage(rect_hover))
        self.resize_image()

        print(f"rectangle size {self.rect_start, self.rect_end}")

        result = inference_segmentor(self.model, self.img[self.rect_start[1]: y, self.rect_start[0]: x, :])

        idx = np.argwhere(result[0] == 1)
        y_idx, x_idx = idx[:, 0], idx[:, 1]
        x_idx = x_idx + self.rect_start[0]
        y_idx = y_idx + self.rect_start[1]

        self.label[y_idx, x_idx] = 1
        
        self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
        self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        self.pixmap = QPixmap(cvtArrayToQImage(rect_hover))
        self.resize_image()


        
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


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.ControlKey = True
            print(self.ControlKey)
          
         

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.ControlKey = False
            print(self.ControlKey)
           
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
