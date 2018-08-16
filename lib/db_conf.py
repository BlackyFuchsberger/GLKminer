# -*- coding: utf-8 -*-
"""Define settings for the database connection

@author: Malte Persike
"""

from collections import namedtuple


# Specify database backend to use
DB_BACKEND_MONGO = 'mongodb'
DB_BACKEND_SQLITE = 'sqlite'

DB_USE_BACKEND = DB_BACKEND_MONGO


# Declare configuration tuples for database access
mongo_config = namedtuple('mongoDB', ['host',
                                      'name',
                                      'password',
                                      'prefix',
                                      'port',
                                      'username'])

sqlite_config = namedtuple('DB', ['name'
                                  'password',
                                  'prefix',
                                  'url',
                                  'username'])


# Make the current database configuration tuple available as "dbconfig"
if DB_USE_BACKEND.casefold() == DB_BACKEND_SQLITE:
    dbconfig = sqlite_config(
            name = 'GLKminer',
            password = '',
            prefix = 'GLKM_',
            url = '../db/glk_applications_v01.db',
            username = ''
            )
else:
    dbconfig = mongo_config(
            host = 'localhost',
            name = 'GLKminer',
            password = 'glkuDB_18',
            prefix = 'GLKM_',
            port = 27017,
            username = 'glkuser'
            )
