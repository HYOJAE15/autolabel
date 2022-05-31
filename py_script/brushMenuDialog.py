from PyQt5.QtWidgets import *
from PyQt5 import uic
from utils import *

# 메인에서 다른 모듈 임포트 해서 사용하자! 
# 메인에서 다른 모듈 의 매서드 활용하자!
#from MainWindow import MainWindow



project_ui = '../ui_design/brushMenuDialog.ui'

form = resource_path(project_ui)
form_class_BrushMenu = uic.loadUiType(form)[0]


class BrushDialog (QDialog, form_class_BrushMenu):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        self.BrushSize = 0
        self.use_brush = False
        print(f"Brush Module self.use_brush {self.use_brush}")
        
        # Brush Menu Buttons
        self.brush_1.clicked.connect(self.brushSize_1)
        self.brush_3.clicked.connect(self.brushSize_3)
        self.brush_5.clicked.connect(self.brushSize_5)
        self.brush_7.clicked.connect(self.brushSize_7)


    def brushSize_1(self):
        # BrushDialog 에서 얻은 값을 MainWindow 에서 BrushDialog 클래스의 인스턴스 값으로 받아서 사용 
        self.BrushSize = 1
        self.use_brush = 1 - self.use_brush
        print(self.use_brush)
        self.close()
        # show 로 띄우니 화면이 여러개 띄워진다
        # self.show()

    def brushSize_3(self):

        self.BrushSize = 3    
        self.close()

    def brushSize_5(self):

        self.BrushSize = 5
        self.close()

    def brushSize_7(self):
        
        self.BrushSize = 7
        self.close()

        



    
    
    #def OpenBrushMenuTest(self):
        #self.show()

        # self.brush_1.clicked.connect(MainWindow.test)


    