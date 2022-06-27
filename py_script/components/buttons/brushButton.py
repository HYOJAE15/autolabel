

import cv2
import sys

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.utils import *
from components.dialogs.brushMenuDialog import BrushMenu

class BrushButton :
    def __init__(self) :
        super().__init__()
        


    def setFalseUseBrush(self):
        self.use_brush = False
    
    def setBrushSize(self):
        self.brushSize = self.brushMenu.brushSize

    def applyBrushSize(self, X, Y): 

        width = int(self.brushSize / 2)
        
        return_x = []
        return_y = []

        _Y, _X = np.mgrid[-width:width, -width:width]
        _Y, _X = _Y.flatten(), _X.flatten()
        _Y, _X = np.squeeze(_Y), np.squeeze(_X)

        if self.circle :
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
        
    def updateBrushState(self):
        
        self.use_brush = True
        # 효재: 자료형에서 int 형과 bool 형 차이 없이 '0'(int)이면 False(bool)인가??
        # 병현: 응 맞아 ㅋㅋ 
        print(f"type_self.use_brush {type(self.use_brush)}")
        print(f"self.use_brush {self.use_brush}")
        print(f"self.set_roi {self.set_roi}")


    def brushPressOrReleasePoint(self, event):

        x, y = getScaledPoint(event, self.scale)
        print(f" getsclaePoint {x, y} ")
        
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

         
         
