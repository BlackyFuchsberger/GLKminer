# -*- coding: utf-8 -*-
"""Provide a variety of functions for file handling.

@author: Malte Persike
"""

# Python core modules and packages
import logging, math, os, re, unicodedata, uuid
from binascii import b2a_hex

# Constants and other objects
logger = logging.getLogger(__name__)


# Function definitions
def collectFiles(folder, regex, subfolders=True):
    """Collect files matching the given regular expression in a folder and
    optionally its subfolders.
       
    Args:
        folder (str): the folder in which to search for files.
        regex (str): a regular expression identifying the files to collect
        subfolders (bool, optional): Whether or not to traverse the
            subfolders of the specified folder. Defaults to True.

    Returns:
        list (str): all found files
    """
    
    filelist = []
    for root, dirs, files in os.walk(folder):
        for f in files:
            if re.search(regex, f, re.IGNORECASE):
                filelist+= [os.path.join(root, f)]

    return filelist


def determineImagetype(stream_first_4_bytes):
    """Determine the image file type based on the magic number comparison
    of the first 4 (or 2) bytes.
    
    Args:
        stream_first_4_bytes (bytes): magic number extracted from the image.

    Returns:
        str: file extension according to the image type.
    """
    
    file_type = None
    bytes_as_hex = b2a_hex(stream_first_4_bytes)
    if bytes_as_hex.startswith('ffd8'):
        file_type = '.jpeg'
    elif bytes_as_hex == '89504e47':
        file_type = ',png'
    elif bytes_as_hex == '47494638':
        file_type = '.gif'
    elif bytes_as_hex.startswith('424d'):
        file_type = '.bmp'
        
    return file_type


def divineImagefile(src_name='', number=None, count=None, number_prefix=None, ext=None):
    """Construct an image file name from  the source file name.
    
    Args:
        src_name (str, optional): The name of the PDF file from which the
            images are extracted.
        number (int, optional): A running number for the file.
        count (int, optional): The maximun running number for all files.
        ext (str, optional): the file type extension for the file name.
    
    Returns:
        str: image file name.
    """

    if ext:
        if not ext.startswith('.'):
            ext = '.'+ext
    else:
        ext = ''

    if not number_prefix:
        number_prefix = ''
        
    if isinstance(count, int):
        count_formatstr = ':0{0}d'.format(max([math.ceil(math.log(max([count, 0]) + 1, 10)), 1]))
    else:
        count_formatstr = ''
    
    if isinstance(number, int):
        number_str = ('_{0}{1'+count_formatstr+'}').format(number_prefix, abs(number))
    else:
        number_str = ''

    file_name = ''
    while not file_name or os.path.exists(file_name):
        file_name = '{0}{1}_{2}{3}'.format(os.path.splitext(os.path.basename(src_name))[0], number_str, uuid.uuid4().hex, ext)
    
    return unicodedata.normalize('NFKD', file_name).encode('ASCII', 'ignore').decode()


def divineImagefolder(basefolder='.', filename='', as_subfolder=False, create=False):
    """Compile the folder path where extracted image files are to be stored.
    Also, create the folder if requested.
    
    Args:
        src_name (str, optional): The full path of the PDF file from which the
            images are extracted.
        options (ImportOptions, optional): settings for image storing.
        create (bool, optional): create the divined folder.
    
    Returns:
        str: path to the image folder.
    """
    
    # Compile name
    if as_subfolder and filename:
        img_folder = os.path.join(basefolder, os.path.splitext(os.path.split(filename)[-1])[0])
    elif basefolder:
        img_folder = basefolder
    else:
        img_folder = '.'

    # Sanitize name
    img_folder = unicodedata.normalize('NFKD', img_folder).encode('ASCII', 'ignore').decode()
    
    # Verify target path before saving
    if create and not os.path.isdir(img_folder):
        os.makedirs(img_folder)
    
    return img_folder


def writeFile (fullpath, data, flags='w'):
    """Write the file data to the filepath.

    Args:
        fullpath (str): full path to the file.
        data (var): data to be saved in the file.
        flags (str): mode for the open() command, e.g., 'w' for write text,
            'wb' for write binary, 'a' for append.
    Returns:
        bool: True if file was successfully saved, False otherwise.
    """

    result = False
    if os.path.isdir(os.path.dirname(fullpath)):
        try:
            file_obj = open(fullpath, flags)
            file_obj.write(data)
            file_obj.close()
            result = True
        except IOError as e:
            logger.exception(e)

    return result
