
import sys 
import os 

from PyQt5 import uic

def load_ui_path(relative_path, file=None): 
    """Get absolute path to resource, works for dev and for PyInstaller 

    Args :
        relative_path (str)
    
    Returns :  
        abs_path (str)
    """ 

    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 

    abs_path = os.path.join(base_path, relative_path)
    
    return abs_path

def load_ui(name):
    """Load UI file and return UI object
    Args:
        name (str): name of ui file to load 
    
    Returns: 
        ui (object)
    """

    ui_path = load_ui_path(name)
    ui = uic.loadUiType(ui_path)[0]
    return ui
