# -*- coding: utf-8 -*-
"""Provide helper functions for the pdfminer package

@author: Malte Persike
"""

# Python core modules and packages
import os, logging, math, unicodedata, uuid
from binascii import b2a_hex
# Third party modules and packages
from pdfminer.layout import LTFigure, LTImage, LTTextBox, LTTextLine
# Local modules and packages
from lib.import_conf import DEFAULT_IMGFOLDER, DEFAULT_IMPORTOPTIONS, DEFAULT_LOGNAME

# Constants and other objects
logger = logging.getLogger(DEFAULT_LOGNAME)

# Function definitions
def divine_imagefolder(src_name='', options=DEFAULT_IMPORTOPTIONS, create=False):
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
    if options.createSubfolders and src_name:
        img_folder = os.path.join(options.imageFolder, os.path.splitext(os.path.split(src_name)[-1])[0])
    elif options.imageFolder:
        img_folder = options.imageFolder
    else:
        img_folder = DEFAULT_IMGFOLDER

    # Sanitize name
    img_folder = unicodedata.normalize('NFKD', img_folder).encode('ASCII', 'ignore').decode()
    
    # Verify target path before saving
    if create and not os.path.isdir(img_folder):
        os.makedirs(img_folder)
    
    return img_folder

def divine_imagefile(src_name='', number=None, count=None, number_prefix=None, ext=None):
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
                     
def determine_image_type(stream_first_4_bytes):
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


def write_file (fullpath, data, flags='w'):
    """Write the file data to the filepath

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


def save_image (lt_image, src_fullpath, page_number=None, options=DEFAULT_IMPORTOPTIONS):
    """Save the image data from an LTImage object, and return the file name,
    if successful.
    
    Args:
        lt_image (LTImage): image object.
        fullpathname (str): filename with path but withour extension where
            the image is to be stored.
    
    Returns:
        str: full path to the stored image.
    """
    
    result = None
    if lt_image.stream:
        # Prepare variables
        file_stream = lt_image.stream.get_rawdata()
        file_ext = determine_image_type(file_stream[0:4])
        
        imgfolder = divine_imagefolder(src_fullpath, options, create=True)
        imgfile = divine_imagefile(src_fullpath, number=page_number, number_prefix='IMG', ext=file_ext)
        imgfullpath = os.path.join(imgfolder, imgfile)
        
        # Save image file
        if write_file(imgfullpath, lt_image.stream.get_rawdata(), flags='wb'):
            result = imgfullpath

    return result


def parse_lt_objs(lt_objs, src_fullpath, page_number, options=DEFAULT_IMPORTOPTIONS, text=[]):
    """Iterate through the list of LT* objects and capture the text or image
    data contained in each.
    
    Args:
        lt_objs (layout.LT*): layout object in a PDF page.
        page_number (int): the page number from where the lt_objs stem.
        image_folder (str): the path where to store extracted images
        text (list): a list of str to which to append the extracted text.

    Returns:
        str: text extracted from the PDF.
    """

    text_content = text
    for lt_obj in lt_objs:
        if isinstance(lt_obj, (LTTextBox, LTTextLine)):
            text_content.append(lt_obj.get_text())
        elif options.saveImages and isinstance(lt_obj, LTImage):
            # an image, so save it to the designated folder, and note it's place in the text
            saved_file = save_image(lt_obj, src_fullpath, page_number, options)
            if saved_file:
                # use html style <img /> tag to mark the position of the image within the text
                text_content.append('<img src="'+saved_file+'" />')
            else:
                logger.error("Error saving image <{0}> on page {1}.".format(lt_obj.__repr__, page_number))
        elif options.saveImages and isinstance(lt_obj, LTFigure):
            # LTFigure objects are containers for other LT* objects, so recurse through the children
            text_content.append(parse_lt_objs(lt_obj.objs, src_fullpath, page_number, options, text_content))

    return '\n'.join(text_content)
