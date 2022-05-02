import os 
import sys

def resource_path(relative_path): 
    """ 
    Get absolute path to resource, works for dev and for PyInstaller 

    Args :
        relative_path (str)
    
    Return 
        abs_path (str)
    """ 
    
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))) 
    abs_path = os.path.join(base_path, relative_path)
    
    return abs_path

