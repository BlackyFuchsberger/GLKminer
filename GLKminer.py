# -*- coding: utf-8 -*-
"""Start the GLKminer framework (provisional).

This is a very provisional file to call different modules of the GLKminer
framework. The goal should be to provide a GUI from where GLKminer is run.

Required Packages:
    A number of third party packages and binaries need to be installed for
    GLKminer to work. These are;

    Packages:
        opencv: Open Source Computer Vision Library
            (https://github.com/opencv/opencv)
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
        Tesseract: Open Source OCR framework
            (Windows installer: https://github.com/UB-Mannheim/tesseract/wiki)

Database Backend:
    The framework runs on a mongoDB database backend. Settings are
    configured in lib.db_settings.py.

@author: Malte Persike
"""

# Python core modules and packages
import logging, os

# Preload local modules
import lib.db_conf as dbc
from lib.db_conf import dbconfig

# Third party modules and packages
if dbc.DB_USE_BACKEND == dbc.DB_BACKEND_MONGO:
    from pymongo import MongoClient
elif dbc.DB_USE_BACKEND == dbc.DB_BACKEND_SQLITE:
    import sqlite3    # Currently nonfunctional

# Local modules and packages
import lib.constants as constants
from lib.importing import importFolder
from lib.import_conf import DEFAULT_IMPORTOPTIONS, DEFAULT_LOGNAME
from lib.wordcloud_helper import createWordcloud

# Toggle logging
if constants.DEFAULT_LOGTOCONSOLE:
    logging.basicConfig(level=logging.INFO)
    for logname in ['pdfminer.pdfdocument','pdfminer.pdfpage','pdfminer.pdfinterp','pdfminer.converter','pdfminer.cmapdb']:
        logging.getLogger(logname).setLevel(logging.WARNING)
logger = logging.getLogger(DEFAULT_LOGNAME)


# Establish connection to database
client = MongoClient('mongodb://{0}:{1}@{2}:{3}/{4}'.format(dbconfig.username, dbconfig.password, dbconfig.host, dbconfig.port, dbconfig.name))
db = client[dbconfig.name]


# Populate database with content from PDF files
if False:
    count = importFolder(folder=os.path.join('..', 'Container', '01_InnovLP'), db=db.GLKM_innovativelehrprojekte)
    logger.info('{0} files were imported from "01_InnovLP".'.format(count))
    
    count = importFolder(folder=os.path.join('..', 'Container', '02_LFS'), db=db.GLKM_lehrfreisemester)
    logger.info('{0} files were imported from "02_LFS".'.format(count))


# Create a wordcloud
createWordcloud(
        '.\\mywordcloud.png',
        os.path.join(DEFAULT_IMPORTOPTIONS.imageFolder, 'cloud_template.png'),
        filter={'content_source': {'$regex': 'text', '$options': 'i'}},
        coll=db.GLKM_innovativelehrprojekte
        )
    

# Cleanup
client.close()
