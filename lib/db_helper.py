# -*- coding: utf-8 -*-
"""Define helper functions for database handling

@author: Malte Persike
"""

# Python core modules and packages
import logging, os
from datetime import datetime

# Constants and other objects
logger = logging.getLogger(__name__)


# Function definitions
def documentExists(record, db):
    """Test if a document with a given set of identifiers exists in the database.

    Args:
        record (dict): a dictionary defining the identifiers of the document to be matched.
        db: a database object

    Returns:
        bool: True if document exists, False otherwise
    """
    
    cursor = db.find(record)
    if cursor:
        return cursor.limit(1).count()
    else:
        return False


def storeDocument(content, source, filename, db, skipduplicate=False):
    """Store a record in the database.
    
    Args:
        content (str): body of data to be stored.
        source (str): information about the content source
        filename (str): full path to the PDF file.
        db: a database object.
        skipduplicate (bool, optional): whether to skip possible duplicates.

    Returns:
        bool: True if storing successful, False otherwise.
    """

    # Compile document and duplicate token
    document = {
            'content_name': os.path.basename(filename),
            'content_URL': os.path.dirname(filename),
            'filecreated_date': str(datetime.fromtimestamp(os.stat(filename).st_ctime)),
            'filemodified_date': str(datetime.fromtimestamp(os.stat(filename).st_mtime)),
            'imported_date': str(datetime.now()),
            'content_source': source,
            'content': content
            }
    
    # Record for duplicate check
    record = {key: document[key] for key in ['content_name', 'filecreated_date']}
    
    # Check if record exists and store if not.
    stored = False
    docexists = documentExists(record, db)
    if skipduplicate and docexists:
        logger.warning('Possible duplicate database entry found. Content was not stored in database.\nDuplicate information: ' + record)
    elif content:
        stored = db.insert_one(document).acknowledged
        if docexists:
            logger.info('Possible duplicate database entry found.\nDuplicate information: ' + record)
        logger.info("Content for file {0} stored in database.".format(filename))

    return stored
