# -*- coding: utf-8 -*-
"""Define settings for the database connection

@author: Malte Persike
"""

from collections import namedtuple

db_settings = namedtuple('DB', ['name',
                                'ext',
                                'password',
                                'tableprefix',
                                'url',
                                'username'])

dbs = db_settings(name = 'glk_applications_v01',
                  ext = '.db',
                  tableprefix = 'GLKMINER_',
                  url = '../db',
                  username = '',
                  password = '')
