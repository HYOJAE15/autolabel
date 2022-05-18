# Customizing QToolButton 
# RoiAutoLabelQToolButtonModule.py

from PyQt5.QtWidgets import *

# RoiAutoLabelButton class (custom QToolButton), object name = roiAutoLabelButton
# widget custom 시 초기설정, 초기화 진행시 매개변수 설정


class RoiAutoLabelButton(QToolButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    

    def Buttonclicked(self):
        print("Roi Button Click!")




