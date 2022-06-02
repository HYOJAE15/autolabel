from lib2to3.pytree import type_repr
import sys
import cv2
import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils import *
from brushMenuDialog import BrushDialog

import sys 
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
        self.vtest = 1
        self.eraserButton.clicked.connect(self.fvtest)
    
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
        self.ControlKey = False
        self.scale = 1
        self.zoomInButton.clicked.connect(self.on_zoom_in)
        self.zoomOutButton.clicked.connect(self.on_zoom_out)
        
        self.zoomInButton.setShortcut("Ctrl+MouseWheel ")

        # brush tools

        # Brush size 3개 지정 해서 몇 픽셀 씩 할것이냐 모르겠다
        #self.BrushMenu = QMenu() 
        #self.BrushMenu.addAction("BrushSize_1", self.BrushSize_1)
        #self.BrushMenu.addAction("BrushSize_2", self.BrushSize_2)
        #self.BrushMenu.addAction("BrushSize_3", self.BrushSize_3)
        #self.brushButton.setMenu(self.BrushMenu)
        #self.brushButton.clicked.connect(self.showBrushMenu)
        #   self.brushButton.clicked.connect(self.updateBrushState) -> 요걸로 use_brush 를 True 로 설정 
        self.brushButton.clicked.connect(self.openBrushMenuDialog)
        self.mainImageViewer.mousePressEvent = self.mousePressEvent
        self.mainImageViewer.mouseMoveEvent = self.mouseMoveEvent
        self.mainImageViewer.mouseReleaseEvent = self.mouseReleaseEvent

        # 다른 모듈 안의 ui 도 import 시키면 ui 연동 가능??
        # ㄴㄴ 안됨
        #self.brush_1.clicked.connect(self.test)

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

    def fvtest(self):
        self.vtest = 23
        print(f"after vtest {self.vtest}")

    def test(self):
        print("가능")
    

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



        # openFolder 메뉴를 클릭 했을 때 getopenfilename 으로 파일 을 불러오고 그 해당 현재 주소를 가지고 
        # treeview 생성??
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
        
        self.label[y, x] = self.label_class 
        self.colormap[y, x] = self.img[y, x] * self.alpha + self.label_palette[self.label_class] * (1-self.alpha)
        self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))


        # BrushDialog 클래스 인스턴스 에서 받은 값으로 사용 하는대 use_brush 값을 생성한 BCI 로 받는 것이 맞나 ?? 무언가 아닌듯...
        # 일단 BrushDialog 클래스 인스턴스 로 생성한 BCI 로 지정후 사용 
        # 아니네 self.use_brush 변수를 다시 지정 해주면 되네
    def mousePressEvent(self, event):

        print(f"position {event.pos()}")
        print(f"after vtest {self.vtest}")

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

    
        # Brush 사이즈 조절, 좌표 불러올때 해당 좌표 + 몇 Pixel 씩 해주면 가능??
    def BrushSize_1(self) :
        #print("BrushSize_1")
        # use_Brush default 값이 false '0' 이니까 
        self.brushButton.setChecked(True)
        self.use_brush = True
        print(type(self.use_brush))
        

     

    def BrushSize_2(self) :
        print("BrushSize_2")
        self.brushButton.setChecked(True)
        self.use_brush = True
        


    def BrushSize_3(self):
        print("BrushSize_3")
        self.brushButton.setChecked(True)
        self.use_brush = True
        

    def showBrushMenu(self) :
        
        self.brushButton.showMenu()
        
    def updateBrushState(self):
        
        self.use_brush = 1 - self.use_brush
        # 자료형에서 int 형과 bool 형 차이 없이 '0'(int)이면 False(bool)인가??
        print(f"type_self.use_brush {type(self.use_brush)}")
        print(f"self.use_brush {self.use_brush}")
        print(f"self.set_roi {self.set_roi}")
         

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
            
            

            
        
    


    def ctrl_zoom_out(self, e):
        if e.key() == Qt.Key_Control :
            self.ControlKey = True


    def resize_image(self):
        size = self.pixmap.size()
        print(f"self.pixmap.size() {self.pixmap.size()}")
        self.scaled_pixmap = self.pixmap.scaled(self.scale * size)
        
        print(f"self.scaled_pixmap{self.scaled_pixmap}")
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
