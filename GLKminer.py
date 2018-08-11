# -*- coding: utf-8 -*-
"""Start the GLKminer framework

@author: Malte Persike
"""

import sqlite3, os
from lib.db_settings import dbs
from lib.db_helper import db_init

# Establish connection to database
db = sqlite3.connect(os.path.join(dbs.url, dbs.name+dbs.ext))
cur = db.cursor()

# Make sure database is populated with tables
if not db_init(db, dbs.tableprefix):
    print("Nein. Nein. Nein. Nein. Nein.")

# Do stuff
#...

# Cleanup
db.commit()
db.close()