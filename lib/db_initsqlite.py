# -*- coding: utf-8 -*-
"""Initialize sqlite database. This module is currently not active.

@author: Malte Persike
"""


def db_init(db, tableprefix=''):
    """Populate applications database with all required tables
    
    Args:
        db (sqlite3.Connection): An open sqlite3 database.
        tableprefix (str, optional): A prefix to prepend to the names of all created tables. Defaults to an empty string.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cur = db.cursor()
        
        cur.execute("""CREATE TABLE IF NOT EXISTS {0} (
                       ID          INTEGER PRIMARY KEY AUTOINCREMENT,
                       TYPE        INTEGER             NOT NULL,
                       DATECREATED INTEGER             NOT NULL,
                       NAME        TEXT,
                       TITLE       TEXT,
                       BODY        TEXT
                       );""".format(tableprefix+'items'))

        cur.execute("""CREATE TABLE IF NOT EXISTS {0} (
                       ID          INTEGER PRIMARY KEY AUTOINCREMENT,
                       NAME        TEXT,
                       SUBTYPE     TEXT,
                       DESCRIPTION TEXT
                       );""".format(tableprefix+'granttypes'))
        
        

        db.commit()
        
        cur.execute("""INSERT INTO {0} (NAME,SUBTYPE,DESCRIPTION) VALUES (
                       'Innovatives Lehrprojekt',
                       'Einzelprojekt',
                       'Themenunabhängige Lehrprojekte, die im Erfolgsfall Modellcharakter für das Fach oder die Fachkultur haben.'
                       );""".format(tableprefix+'granttypes'))

        cur.execute("""INSERT INTO {0} (NAME,SUBTYPE,DESCRIPTION) VALUES (
                       'Innovatives Lehrprojekt',
                       'Schwerpunktprojekt',
                       'Themengebundene Lehrprojekte, die im Erfolgsfall Modellcharakter für das Fach oder die Fachkultur haben.'
                       );""".format(tableprefix+'granttypes'))

        cur.execute("""INSERT INTO {0} (NAME,SUBTYPE,DESCRIPTION) VALUES (
                       'Lehrfreisemester',
                       '',
                       'Freistellung von Regelaufgaben in der Lehre für Projekte, die einen Beitrag zur Weiterentwicklung der Lehre liefern'
                       );""".format(tableprefix+'granttypes'))

        db.commit()
        
        return True
    except:
        return False
