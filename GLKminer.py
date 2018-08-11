# -*- coding: utf-8 -*-
"""Start the GLKminer framework

mongoDB
    user: glkuser
    pw: glkDB_18

@author: Malte Persike
"""

# Python core modules and packages
import os

# Third party modules and packages
from pymongo import MongoClient

# Local modules and packages
from lib.db_settings import dbs
from lib.fileutil import CollectFiles


# Establish connection to database
client = MongoClient('mongodb://{0}:{1}@{2}:{3}/{4}'.format(dbs.username, dbs.password, dbs.host, dbs.port, dbs.name))
db = client[dbs.name]


filelist = CollectFiles(os.path.join('..', 'Container'), '\.pdf$')
ImportFiles(filelist, db)

# Cleanup
client.close()
