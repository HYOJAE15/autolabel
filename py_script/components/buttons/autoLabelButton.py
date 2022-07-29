
from cmath import e
import cv2
import sys

import numpy as np 

from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.utils import *

sys.path.append("./dnn/mmsegmentation")
from mmseg.apis import inference_segmentor



class AutoLabelButton :
    def __init__(self) :
        super().__init__()



    def roi256(self):
        print("roi256")
        self.brushButton.setChecked(False)
        self.roiAutoLabelButton.setChecked(True)

        self.use_brush = False

        self.use_erase = False

        self.set_roi = False

        self.set_roi_256 = True


    def roiRec(self):
        self.brushButton.setChecked(False)
        self.roiAutoLabelButton.setChecked(True)
        print(f"self.use_brush {self.use_brush}")

        self.use_brush = False

        self.use_erase = False

        self.set_roi = True
        
        self.set_roi_256 = False

        print(f"self.set_roi {self.set_roi}")
        print(f"self.use_brush {self.use_brush}")


    def roi256PressPoint(self, event):

        try : 

            x, y = getScaledPoint(event, self.scale)
            if x < 128 and y < 128 :
                print("x < 128 and y < 128")
                self.rect_start = 0, 0
                print(self.rect_start)
                print(type(self.rect_start))
                self.rect_end = x+128, y+128
            elif x < 128 :
                print("x < 128")
                self.rect_start = 0, y-128
                self.rect_end = x+128, y+128
            elif y < 128 :
                print("y < 128")
                self.rect_start = x-128, 0
                self.rect_end = x+128, y+128 
            else :
                print("dang")
                self.rect_start = x-128, y-128
                self.rect_end = x+128, y+128

            
            result = inference_segmentor(self.model_list[self.label_segmentation-1], self.img[self.rect_start[1]: self.rect_end[1],
                                            self.rect_start[0]: self.rect_end[0], :])

            print(f'modelListindex {self.label_segmentation-1}')

            cv2.imshow("cropImage", self.img[self.rect_start[1]: self.rect_end[1],
                                            self.rect_start[0]: self.rect_end[0], :])
            

            print(f'cropImage.shape {self.img[self.rect_start[1]: self.rect_end[1], self.rect_start[0]: self.rect_end[0], :].shape}')
            

            idx = np.argwhere(result[0] == 1)
            y_idx, x_idx = idx[:, 0], idx[:, 1]
            x_idx = x_idx + self.rect_start[0]
            y_idx = y_idx + self.rect_start[1]

            self.label[y_idx, x_idx] = self.label_segmentation # label_palette 의 인덱스 색깔로 표현
            
            self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
            self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
            self.resize_image()


            thickness = 2    

            rect_256 = cv2.rectangle(
                self.colormap.copy(), self.rect_start, self.rect_end, (255, 255, 255), thickness)

            print(f"rectangle size {self.rect_start, self.rect_end}")
            self.pixmap = QPixmap(cvtArrayToQImage(rect_256))
            self.resize_image()
            
        except ZeroDivisionError as e :
            print(e)

        
    def roiPressPoint(self, event):

        x, y = getScaledPoint(event, self.scale)

        self.rect_start = [x, y]

    def roiMovingPoint(self, event):

        x, y = getScaledPoint(event, self.scale)

        self.rect_end = [x, y]

        thickness = 5

        rect_hover = cv2.rectangle(
            self.colormap.copy(), self.rect_start, self.rect_end, (255, 255, 255), thickness) # , color, thickness, lineType,)
        self.pixmap = QPixmap(cvtArrayToQImage(rect_hover))
        self.resize_image()
        

    def roiReleasePoint(self, event):

        x, y = getScaledPoint(event, self.scale)
    
        if x < self.rect_start[0] : 
            temp = x 
            x = self.rect_start[0]
            self.rect_start[0] = temp 
            
        if y < self.rect_start[1] : 
            temp = y 
            y = self.rect_start[1]
            self.rect_start[1] = temp 

        self.rect_end = [x, y] 

        if (self.rect_end[0] == self.rect_start[0]) | (self.rect_end[1] == self.rect_start[1]):
            self.rect_start[0] -= int(128/self.scale)
            self.rect_start[1] -= int(128/self.scale)  

            self.rect_end[0] += int(128/self.scale) 
            self.rect_end[1] += int(128/self.scale) 

        self.rect_start[0] = np.clip(self.rect_start[0], 0, self.label.shape[1])
        self.rect_start[1] = np.clip(self.rect_start[1], 0, self.label.shape[0])

        self.rect_end[0] = np.clip(self.rect_end[0], 0, self.label.shape[1])
        self.rect_end[1] = np.clip(self.rect_end[1], 0, self.label.shape[0])
            

        result = inference_segmentor(self.model_list[self.label_segmentation-1], self.img[self.rect_start[1]: y, self.rect_start[0]: x, :])

        idx = np.argwhere(result[0] == 1)
        y_idx, x_idx = idx[:, 0], idx[:, 1]
        x_idx = x_idx + self.rect_start[0]
        y_idx = y_idx + self.rect_start[1]

        self.label[y_idx, x_idx] = self.label_segmentation
        
        self.colormap = blendImageWithColorMap(self.img, self.label, self.label_palette, self.alpha)
        self.pixmap = QPixmap(cvtArrayToQImage(self.colormap))
        self.resize_image()

    

        
    
