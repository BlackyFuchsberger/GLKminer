# -*- coding: utf-8 -*-
"""Provide a variety of functions for file handling.

@author: Malte Persike
"""

import os, re


def collectFiles(folder, regex, subfolders=True):
    """Collect files matching the given regular expression in a folder and
    optionally its subfolders.
       
    Args:
        folder (str): the folder in which to search for files.
        regex (str): a regular expression identifying the files to collect
        subfolders (bool, optional): Whether or not to traverse the
            subfolders of the specified folder. Defaults to True.

    Returns:
        list (str): all found files
    """
    
    filelist = []
    for root, dirs, files in os.walk(folder):
        for f in files:
            if re.search(regex, f, re.IGNORECASE):
                filelist+= [os.path.join(root, f)]

    return filelist
