
from PyQt5 import QtCore

from components.dialogs.brushMenuDialog import BrushMenu
from components.dialogs.eraseMenuDialog import EraseMenu
from components.dialogs.setCategoryDialog import setCategoryDialog



class dialogOpener :
    def __init__(self) :
        super().__init__()


    ########################### 
    ### Dialog Opener ###
    ###########################

    def openCategoryInfoDialog(self, event):

        self.newProjectDialog.close()

        self.setCategoryDialog = setCategoryDialog()
        self.setCategoryDialog.createButton.clicked.connect(self.createProjectHeader)
        self.setCategoryDialog.exec()


    def openBrushDialog(self, event):

        if hasattr(self, 'brushMenu'):
            self.brushMenu.close()

        self.use_brush = True
        self.brushButton.setChecked(True)
        self.roiAutoLabelButton.setChecked(False)
        print(f" openBrushDialog {self.brushSize}")
        self.brushMenu = BrushMenu()
        self.brushMenu.lineEdit.setText(f'{self.brushSize} px')
        if self.brushSize > 2 :
            print("brushSize > 2") 
            self.brushMenu.horizontalSlider.setValue(self.brushSize)
            self.brushMenu.lineEdit.setText(f'{self.brushSize} px')

        self.initBrushTools()
        self.brushMenu.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.brushMenu.show()

        #좌표를 받고 싶다면 mousePressEvent 활용
        self.brushMenu.move(self.pos())

        if self.circle :
            self.brushMenu.circleButton.setChecked(True)
            self.brushMenu.squareButton.setChecked(False)
        elif self.circle == False :
            self.brushMenu.squareButton.setChecked(True)
            self.brushMenu.circleButton.setChecked(False)

        
    def openEraseDialog(self, event):
        print("erase")
        self.eraseButton.setChecked(True)
        self.use_erase = True
        self.eraseMenu = EraseMenu()
        self.eraseMenu.eraselineEdit.setText(f'{self.eraseSize} px')
        if self.eraseSize > 2 :
            print("eraseSize > 2") 
            self.eraseMenu.erasehorizontalSlider.setValue(self.eraseSize)
            self.eraseMenu.eraselineEdit.setText(f'{self.eraseSize} px')
        
        self.eraseMenu.move(self.pos())
        self.initEraseTools()
        self.eraseMenu.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.eraseMenu.show()


                        
    def initEraseTools(self):
        self.eraseMenu.erasehorizontalSlider.valueChanged.connect(self.setEraseSize)

    def initBrushTools(self):
        self.brushMenu.horizontalSlider.valueChanged.connect(self.setBrushSize)
        self.brushMenu.circleButton.clicked.connect(self.setBrushCircle)
        self.brushMenu.squareButton.clicked.connect(self.setBrushSquare)

    def setBrushCircle(self):
        self.circle = True
        self.brushMenu.circleButton.setChecked(True)
        self.brushMenu.squareButton.setChecked(False)

    def setBrushSquare(self):
        self.circle = False
        self.brushMenu.squareButton.setChecked(True)
        self.brushMenu.circleButton.setChecked(False)
        

