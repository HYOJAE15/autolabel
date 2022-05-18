# Customizing QSlider
# LabelOpacityQSliderModule.py




from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# LabelOpacitySlider class (custom QSlider), object name : labelOpacitySlider
# mouse press, move, release, wheel, 방향키(?)
# 클래스 생성후 초기화 에서 매개변수들 무엇인가??

class LabelOpacitySlider(QSlider) :
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_drag: bool = False

    def mousePressEvent(self, ev: QMouseEvent):
        print("mouse press")
        if ev.button() == Qt.LeftButton:
            ev.accept()
            x = ev.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            self.setValue(int(value))
        else:
            return super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev: QMouseEvent):
        print("mouse move")
        if ev.buttons() & Qt.LeftButton:
            ev.accept()
            x = ev.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            self.setValue(int(value))

            if not self._is_drag:
                self._is_drag = True
        else:
            return super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev: QMouseEvent):
        print("mouse release")
        print(ev.button())
        if ev.button() == Qt.LeftButton and self._is_drag:
            ev.accept()
            self._is_drag = False
            x = ev.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
        else:
            return super().mouseReleaseEvent(ev)
