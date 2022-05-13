from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *





class Canvas(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.drawing = False
        self.brushSize = 28
        self.brushColor = Qt.black
        self.lastPoint = QPoint()
        self.ver_scale = 1
        self.hzn_scale = 1

    # paint event
    def paintEvent(self, event):
		# create a canvas
        canvasPainter = QPainter(self)
		# draw rectangle on the canvas
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

    def readImageFromFile(self, filepath):
        """To be depricated
        """
        self.image = QImage(filepath)
        self.update()

    def readImageFromArray(self, array):

        if len(array.shape) == 3 : 
            h, w, _ = array.shape
        else :
            raise 

        self.image = QImage(array.data, w, h, 3 * w, QImage.Format_RGB888)
        self.update()

    def setVerticalScale(self, new_scale):
        self.ver_scale = new_scale
    
    def setHorizontalScale(self, new_scale):
        self.hzn_scale = new_scale

    # method for checking mouse cicks
    def mousePressEvent(self, event):

		# if left mouse button is pressed
        if event.button() == Qt.LeftButton:
			# make drawing flag true
            self.drawing = True
			# make last point to the point of cursor
            scaled_event_pos = QPoint(event.pos().x()*self.hzn_scale, event.pos().y()*self.ver_scale)
            self.lastPoint = scaled_event_pos

	# method for tracking mouse activity
    def mouseMoveEvent(self, event):
		
		# checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) & self.drawing:
			
			# creating painter object
            painter = QPainter(self.image)
			
			# set the pen of the painter
            painter.setPen(QPen(self.brushColor, self.brushSize,
							Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
			
			# draw line from the last point of cursor to the current point
			# this will draw only one step

            scaled_event_pos = QPoint(event.pos().x()*self.hzn_scale, event.pos().y()*self.ver_scale)
            
            painter.drawLine(self.lastPoint, scaled_event_pos)
			# change the last point
            self.lastPoint = scaled_event_pos
			# update
            self.update()

	# method for mouse left button release
    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
			# make drawing flag false
            self.drawing = False

