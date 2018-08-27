# -*- coding: utf-8 -*-
"""Start the GLKminer framework (provisional).

This is a very provisional file to instantiate and start the GLKminer UI.

Required Packages:
    A number of third party packages and binaries need to be installed for
    GLKminer to work. These are;

    Packages:
        opencv: Open Source Computer Vision Library
            (https://github.com/opencv/opencv)
        kivy: Open source Python library for rapid development of applications
            (https://github.com/kivy/kivy)
        pdfminer: Extract text from extractable PDF documents
            (https://github.com/pdfminer/pdfminer.six)
        pymongo: Python mongoDB driver
            (https://github.com/mongodb/mongo-python-driver)
        PyPDF2: Read and write PDF files with Python
            (https://github.com/mstamy2/PyPDF2)
        pytesseract: Wrapper for the Tesseract API
            (https://github.com/madmaze/pytesseract)
        wand: Wrapper for the ImageMagick API
            (https://github.com/dahlia/wand)
        wordcloud: Generate word clouds from text.
            (https://github.com/amueller/word_cloud)
    Binaries:
        ImageMagick: Open Source image conversion tool. Note that as of August
            2018, wand only supports ImageMagick 6.
            (https://www.imagemagick.org/script/index.php)
        MongoDB: noSQL database engine.
            (https://www.mongodb.com)
        Tesseract: Open Source OCR framework
            (Windows installer: https://github.com/UB-Mannheim/tesseract/wiki)

Database Backend:
    The framework runs on a mongoDB database backend. Settings are
    configured in lib.db_conf.py.

@author: Malte Persike
"""

# Python core modules and packages
import logging

# Local modules and packages
from gui.GLKminerApp import GLKminerApp
import lib.constants as constants


# Toggle logging
if constants.DEFAULT_LOGTOCONSOLE:
    logging.basicConfig(level=logging.INFO)
    for logname in ['pdfminer.pdfdocument','pdfminer.pdfpage','pdfminer.pdfinterp','pdfminer.converter','pdfminer.cmapdb']:
        logging.getLogger(logname).setLevel(logging.WARNING)

# Run the UI from where the currently implemented functions can be invoked
app = GLKminerApp()
app.run()

# Beware that when run in IPython, the kivy framework produces an error on the
# second and every further start of the app. To ensure proper function, the
# console must be restarted before the next run.
exit()
