
import sys 
import os 

def ui_path(relative_path, file=None): 
    """Get absolute path to resource, works for dev and for PyInstaller 

    Args :
        relative_path (str)
    
    Returns :  
        abs_path (str)
    """ 

    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 

    abs_path = os.path.join(base_path, relative_path)
    
    return abs_path