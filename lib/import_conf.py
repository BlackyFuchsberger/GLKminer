# -*- coding: utf-8 -*-
"""Define settings for PDF text import

@author: Malte Persike
"""

# Python core modules and packages
import os
from collections import namedtuple

# Constants
DEFAULT_IMGFOLDER = '.'
DEFAULT_LOGNAME = 'importing'

# Options for importing 
ImportOptions = namedtuple('ImportOptions', [
        'createSubfolders',
        'imageFolder',
        'imageResolution',
        'saveImages'
        ])

DEFAULT_IMPORTOPTIONS = ImportOptions(
        createSubfolders= True,
        imageFolder= os.path.join('.','data','img'),
        imageResolution= 600,
        saveImages= False
        )
