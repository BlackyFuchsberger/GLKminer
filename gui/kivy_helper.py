# -*- coding: utf-8 -*-
"""Helper functions for Kivy GUI framework.

@author: Malte
"""

# Third party modules and packages
from kivy.base import EventLoop
from kivy.cache import Cache
from kivy.core import window

# Function definitions
def reset():
    """Try to reset global variables so that a kivy app can be started more
    than once under IPython.
    
    Status:
        Not functional.
        
    Args:
        None
    
    Returns:
        None
    """
    
    if not EventLoop.event_listeners:
        window.Window = window.core_select_lib('window', window.window_impl, True)
    Cache.print_usage()
    for cat in Cache._categories:
        Cache._objects[cat] = {}
