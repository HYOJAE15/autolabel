# Customizing QToolButton 
# RoiAutoLabelQToolButtonModule.py


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



# RoiAutoLabelButton class (custom QToolButton), object name = roiAutoLabelButton
# widget custom 시 초기설정, 초기화 진행시 매개변수 설정
# QToolButton widget 을 custom 으로 승격 했기에 해당  버튼에 기능을 추가 및 시그널 줘서 실행 object name 설정 불 필요 
# custom 으로 진행시 main 에 임포트 하지 않아도 되고, qt designer 에서 더욱 확장 할 수 있다???? 

# 각 위젯 들 확장은 cusotm 으로 진행 하고, ui 의 서로 다른 widget 끼리 연동이 필요하면
# main 에서 임포트 하여 서로다른 widget 끼리 연동하여 실행 (그러면 custom 하는 이유가 없나 ??)
# custom 을 왜하는 거지?

class RoiAutoLabelButton(QToolButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.setArrowType(Qt.UpArrow)
        self.clicked.connect(self.Buttonclicked)
            
    def Buttonclicked(self):
        print("clicked!")





