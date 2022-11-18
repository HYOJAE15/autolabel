

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from ui_design.__import__ import ui_path

brushMenu_ui = 'setCategoryInfo.ui'

form_brushMenu = ui_path(brushMenu_ui)
form_class_brushMenu = uic.loadUiType(form_brushMenu)[0]

class setCategoryDialog(QDialog, form_class_brushMenu):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        # self.show()

        self.cancelButton.clicked.connect(self.close)
        self.addRowButton.clicked.connect(self.addRow)
        self.deleteRowButton.clicked.connect(self.deleteRow)
        self.tableWidget.clicked.connect(self.eventTable)
        self.tableWidget.doubleClicked.connect(self.eventTable)


    def eventTable(self, item):
        if item.column() != 0: 
            # open color picker 
            color = QColorDialog.getColor()
            self.tableWidget.item(item.row(), 1).setBackground(QColor(color.red(), color.green(), color.blue()))
            self.tableWidget.item(item.row(), 2).setText(f'[{color.red()}, {color.green()}, {color.blue()}]')


    def addRow(self):
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition) #insert new row
        
        for i in range(0, 3):

            item = QTableWidgetItem()
            if i == 0 : 
                item.setText(f"Class{rowPosition}")
            elif i == 1 : 
                item.setText(f"")
            elif i == 2 : 
                item.setText(f"[{rowPosition}, {rowPosition}, {rowPosition}]")

            self.tableWidget.setItem(rowPosition, i, item)
            self.tableWidget.item(rowPosition, i).setTextAlignment(Qt.AlignCenter)
        
        self.tableWidget.item(rowPosition, 1).setBackground(QColor(rowPosition, rowPosition, rowPosition))


    def deleteRow(self):
        self.tableWidget.removeRow(self.tableWidget.currentRow())
        
    

