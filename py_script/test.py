    
    
    def openBrushDialog_tt(self):
        self.brushMenu = BrushMenu()
        self.brushMenu.exec_()
        self.use_brush = self.brushMenu.use_brush
        self.brushSize = self.brushMenu.brushSize

        if self.use_brush:
            self.brushButton.setChecked(True)
            self.roiAutoLabelButton.setChecked(False)
            #self.brushMenu.horizontalSlider.setValue(self.brushSize)
            #self.brushMenu.lineEdit.setText(f'{self.brushSize} px')
            self.brushMenu.horizontalSlider.valueChanged.connect(self.setBrushSize)
        
    def openBrushMenuDialog_tt(self):
        # brushMenuDialog 모듈의 BrushDialog 클래스 에 대한 인스턴스를 생성 
        # BrushDialogClass's Instance
        # 클래스 에 대한 인스턴스로 받아들인 값을 사용한다
        BCI = BrushDialog()
        # exec_ 로 띄워진 화면은 닫기 전 까지는 parent 화면으로 넘어갈수 없다.
        BCI.exec_()
        
        self.BCIValue = BCI.BrushSize
        self.use_brush = BCI.use_brush
        print(f"before self.use_brush {self.use_brush}")
        # 인스턴스로 받아들인 값으로 활용해서 Brush Size 조절 
        

        # 창을 그냥 닫을 시 오류를 피하는 방법...  오류 피할려면 모두 loop 돌려야 ??
        if self.BCIValue:
            self.brushButton.setChecked(True)
            print(f"self.BCIValue = {self.BCIValue}")
            print(f"after self.use_brush {self.use_brush}")

        else :
            self.brushButton.setChecked(False)
            print("Brush Size 를 선택하지 않았습니다.") 