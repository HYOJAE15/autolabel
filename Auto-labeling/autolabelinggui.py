import sys
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import uic
import cv2   # computer vision library 오픈소스 컴퓨터 비전 
import os 

def resource_path(relative_path): 
    """ Get absolute path to resource, works for dev and for PyInstaller """ 
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    return os.path.join(base_path, relative_path)
# import os, import sys  한다음 위 함수 정의 해서 pyinstaller 오류 해결


#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
# pyinstaller 로 하나의 실행파일 생성시 아래와 같이 
form = resource_path("auto-labeling.ui")
form_class = uic.loadUiType(form)[0]

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        #버튼에 기능을 연결하는 코드
        self.btn1.clicked.connect(self.button1Function)
        self.btn2.clicked.connect(self.button2Function)

    #btn_1이 눌리면 작동할 함수, 이미지를 불러오는 함수 
    def button1Function(self) :
        filename = QFileDialog.getOpenFileName(self, 'open image', "C:/", "Images (*.jpg *.psd *.png)")   # 이미지를 불러온다
        imagepath = filename[0]      # 이미지를 변수 에 저장??
        pixmap = QPixmap(imagepath)    
        self.label.setPixmap(QPixmap(pixmap))   # image 를 label 에 표시 한다 (designer 에서 설정해둔 label)
  

    #btn_2가 눌리면 작동할 함수, 이미지를 불러 와서 다음 스텝 영역을 드래그 해서 이미지를 자르자 crop
    def button2Function(self) :
        img = cv2.imread("C:/Users/oh978/Auto-labeling/upload test.jpg")      
        # 왜 인지는 모르겠으나 일부 매개변수 에서는 경로 설정시 '\' 가 아닌 '/' 을 사용 한다. 위 경우가 '/'
        # 리눅스, 파이썬 자세한건 아니지만 여튼 슬래시 인경우와 백슬래시 인 경우 혼동 
        # 상대경로 사용시 pyinstaller 오류, 절대경로 사용 권유
        cv2.namedWindow('image')
        cv2.imshow('image', img)

    # menu 바의 open 에서 file을 누르면 작동하는 file open 함수, QAction 의 함수 설정 
    def openfilemenubarFunction(self) :
        filename = QFileDialog.getOpenFileName(self, 'open image', "/", "Images (*.jpg *.psd *.png)")   # 이미지를 불러온다
        imagepath = filename[0]      # 이미지를 변수 에 저장??
        pixmap = QPixmap(imagepath)   
        self.label.setPixmap(QPixmap(pixmap))




if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()

