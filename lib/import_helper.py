# -*- coding: utf-8 -*-
"""Provide helper functions for the pdfminer package

@author: Malte Persike
"""

# Python core modules and packages
import os, logging
# Third party modules and packages
from pdfminer.layout import LTFigure, LTImage, LTTextBox, LTTextLine
# Local modules and packages
from lib.import_conf import DEFAULT_IMPORTOPTIONS, DEFAULT_LOGNAME
from lib.fileutil import determineImagetype, divineImagefile, writeFile

# Constants and other objects
logger = logging.getLogger(DEFAULT_LOGNAME)


# Function definitions
def saveLtImage (lt_image, src_fullpath, dst_folder='.', page_number=None):
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
        file_ext = determineImagetype(file_stream[0:4])
        
        # Compile file name for saved image
        imgfile = divineImagefile(
                src_name=src_fullpath,
                number=page_number,
                number_prefix='IMG',
                ext=file_ext)
        imgfullpath = os.path.join(dst_folder, imgfile)
        
        # Save image file
        if writeFile(imgfullpath, lt_image.stream.get_rawdata(), flags='wb'):
            result = imgfullpath

    return result


def parseLtObjs(lt_objs, src_fullpath, page_number, dst_folder='.', options=DEFAULT_IMPORTOPTIONS, text=[]):
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
            saved_file = saveLtImage(
                    lt_image=lt_obj,
                    src_fullpath=src_fullpath,
                    dst_folder=dst_folder,
                    page_number=page_number)
            if saved_file:
                # use html style <img /> tag to mark the position of the image within the text
                text_content.append('<img src="'+saved_file+'" />')
            else:
                logger.error("Error saving image <{0}> on page {1}.".format(lt_obj.__repr__, page_number))
        elif options.saveImages and isinstance(lt_obj, LTFigure):
            # LTFigure objects are containers for other LT* objects, so recurse through the children
            text_content.append(parseLtObjs(lt_obj.objs, src_fullpath, page_number, options, text_content))

    return '\n'.join(text_content)
