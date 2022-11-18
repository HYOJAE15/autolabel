import cv2
import sys

import numpy as np 

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from utils.utils import *

# sys.path.append("./dnn/mmsegmentation")
# from mmseg.apis import init_segmentor, inference_segmentor


class DnnModel :
    def __init__(self) :
        super().__init__()



    def crackModel (self):
        
        config_file = './dnn/checkpoints/2022.01.06 cgnet general crack 2048/cgnet_2048x2048_60k_CrackAsCityscapes.py'
        checkpoint_file = './dnn/checkpoints/2022.01.06 cgnet general crack 2048/iter_60000.pth'
        self.model = init_segmentor(config_file, 
                                    checkpoint_file, 
                                    device='cuda:0')


    def efflorescenceModel (self):
        
        config_file_efflorescence = './dnn/checkpoints/2022.07.28_cgnet_1024x1024_concrete_efflorescence/cgnet_1024x1024_60k_cityscapes.py'
        checkpoint_file_efflorescence = './dnn/checkpoints/2022.07.28_cgnet_1024x1024_concrete_efflorescence/cgnet_1024x1024_iter_60000.pth'
        self.model = init_segmentor(config_file_efflorescence, 
                                    checkpoint_file_efflorescence,
                                    device='cuda:0')

    def rebarExposureModel (self):

        config_file_rebarExposure = './dnn/checkpoints/2022.08.05_cgnet_1024x1024_concrete_rebarExposure/cgnet_1024x1024_concrete_rebar_60k_cityscapes.py'
        checkpoint_file_rebarExposure = './dnn/checkpoints/2022.08.05_cgnet_1024x1024_concrete_rebarExposure/iter_60000.pth'
        self.model = init_segmentor(config_file_rebarExposure, 
                                    checkpoint_file_rebarExposure,
                                    device='cuda:0')


    def spallingModel (self):

        config_file_spalling = './dnn/checkpoints/2022.08.06_cgnet_1024x1024_concrete_spalling/cgnet_1024x1024_concrete_spalling_60k_cityscapes.py'
        checkpoint_file_spalling = './dnn/checkpoints/2022.08.06_cgnet_1024x1024_concrete_spalling/iter_60000.pth'
        self.model = init_segmentor(config_file_spalling, 
                                    checkpoint_file_spalling,
                                    device='cuda:0')
