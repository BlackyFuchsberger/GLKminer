# -*- coding: utf-8 -*-
"""The GLKminer UI. As of now, this is only a very rudimentary UI leaving
much to be desired.

@author: Malte Persike
"""

# Python core modules and packages
import os

# Preload local modules
import lib.db_conf as dbc
from lib.db_conf import dbconfig

# Third party modules and packages
if dbc.DB_USE_BACKEND == dbc.DB_BACKEND_MONGO:
    from pymongo import MongoClient
elif dbc.DB_USE_BACKEND == dbc.DB_BACKEND_SQLITE:
    import sqlite3    # Currently nonfunctional

# Local modules and packages
from lib.bagofwords import collectFrequencies
from lib.importing import importFolder
from lib.import_conf import DEFAULT_IMPORTOPTIONS, DEFAULT_LOGNAME
from lib.wordcloud_helper import createWordcloud

# Third party modules and packages
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

# Classes
class MainScreen(GridLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Define UI elements
        self.cols=1
        self.add_widget(Label(text='A very basic main screen.'))
        self.button_dbpopulate = Button(text='Populate database')
        self.button_dbpopulate.bind(on_press=self.doDBPopulate)                                
        self.add_widget(self.button_dbpopulate)
        self.button_createwordcloud = Button(text='Create wordcloud')
        self.button_createwordcloud.bind(on_press=self.doCreateWordcloud) 
        self.add_widget(self.button_createwordcloud)
        
        # Establish connection to database
        self.client = MongoClient('mongodb://{0}:{1}@{2}:{3}/{4}'.format(dbconfig.username, dbconfig.password, dbconfig.host, dbconfig.port, dbconfig.name))


    def doDBPopulate(self, instance):
        """Read a number of PDF files and store their text content in database.
        Note that as of now, both the location of the PDF files and the
        database parameters are hard coded in the script.
    
        Args:
            instance (Widget): the calling UI element.
    
        Returns:
            None
        """
        if (self.client):
            db = self.client[dbconfig.name]
    
            Logger.info('Importing Innovative Lehrprojekte.')
            count = importFolder(folder=os.path.join('..', 'Container', '01_InnovLP'), db=db.GLKM_innovativelehrprojekte)
            Logger.info('{0} files were imported from "01_InnovLP".'.format(count))
            
            Logger.info('Importing Lehrfreisemester.')
            count = importFolder(folder=os.path.join('..', 'Container', '02_LFS'), db=db.GLKM_lehrfreisemester)
            Logger.info('{0} files were imported from "02_LFS".'.format(count))
        else:
            Logger.warning('Non database defined.')


    def doCreateWordcloud(self, instance):
        """Create a wordcloud from text in a document collection.
        Note that as of now, both the location database and the target image
        parameters are hard coded in the script.
    
        Args:
            instance (Widget): the calling UI element.
    
        Returns:
            None
        """
        if (self.client):
            Logger.info('Creating wordcloud.')
            db = self.client[dbconfig.name]
    
            Logger.info('Collecting word frequencies. This may take a while.')
            freqs = collectFrequencies(
                    coll=db.GLKM_innovativelehrprojekte,
                    content_field='content',
                    filter={'content_source': {'$regex': 'text', '$options': 'i'}}
                    )
            
            Logger.info('Assembling word cloud. This may take even longer.')
            createWordcloud(
                    freqs,
                    '.\\mywordcloud.png',
                    os.path.join(DEFAULT_IMPORTOPTIONS.imageFolder, 'cloud_template.png'),
                    )

            Logger.info('Wordcloud created.')
        else:
            Logger.warning('Non database defined.')


class GLKminerApp(App):
    
    def build(self):
        self.app = MainScreen()
        return self.app

    def on_stop(self):
        if self.app.client:
            self.app.client.close()
