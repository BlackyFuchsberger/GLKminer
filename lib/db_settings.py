# -*- coding: utf-8 -*-
"""Define settings for the database connection

@author: Malte Persike
"""

from collections import namedtuple


DB_BACKEND_MONGO = 'mongodb'
DB_BACKEND_SQLITE = 'sqlite'


DB_USE_BACKEND = DB_BACKEND_MONGO

mongo_settings = namedtuple('mongoDB', ['host',
                                        'name',
                                        'password',
                                        'prefix',
                                        'port',
                                        'username'])

sqlite_settings = namedtuple('DB', ['name'
                                    'password',
                                    'prefix',
                                    'url',
                                    'username'])

if DB_USE_BACKEND.casefold() == DB_BACKEND_SQLITE:
    dbs = sqlite_settings(name = 'GLKminer',
                          password = '',
                          prefix = 'GLKMINER_',
                          url = '../db/glk_applications_v01.db',
                          username = '')
else:
    dbs = mongo_settings(host = 'localhost',
                         name = 'GLKminer',
                         password = 'glkuDB_18',
                         prefix = 'GLKM_',
                         port = 27017,
                         username = 'glkuser')
