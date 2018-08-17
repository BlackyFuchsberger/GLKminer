# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 10:25:05 2018

@author: Malte
"""

# Python core modules and packages
import io, logging, os

# Third party modules and packages
import PyPDF2
from wand.image import Image

# Local modules and packages
from lib.fileutil import divineImagefile

# Constants and other objects
DEFAULT_RESOLUTION = 400
logger = logging.getLogger(__name__)


# Function definitions
def savePDFPageAsImage(src_name, dst_folder, pages, filetype, resolution=DEFAULT_RESOLUTION):
    """Load a PDF file and save the given pages to image files.
    
    Args:
        src_name (str): name of the PDF file.
        pages (int|list): pages to save.
        filetype (str): extension indicating the image file format.
        options (ImportOptions): tuple holding various settings.

    Returns:
        int: the number of saved files
    """

    if isinstance(pages, int):
        pages = [pages]

    imgfullpath = ''        
    try:
        fb = open(src_name, "rb")
    except IOError as e:
        logger.error(e)
    else:
        # File opened ok. Let's save them pages
        src_pdf = PyPDF2.PdfFileReader(fb, strict=False)
        typestr = filetype.strip('.')

        # Interate over page numbers and save those pages as single files
        for page in pages:
            # Create a temporary PDF object and copy the given page over.
            dst_pdf = PyPDF2.PdfFileWriter()
            dst_pdf.addPage(src_pdf.getPage(page))

            # Write the temporary PDF to a memory stream
            pdf_bytes = io.BytesIO()
            dst_pdf.write(pdf_bytes)
            pdf_bytes.seek(0)

            # Convert the PDF to an image
            img = Image(file=pdf_bytes, resolution=resolution)
            img.type = 'grayscale'
            img.gaussian_blur(radius=3, sigma=1)
            img.compression = 'losslessjpeg'
            img.convert(typestr)
            
            # Divine a file name, verify folder, and save the image
            imgfile = divineImagefile(
                    src_name=src_name,
                    number=page,
                    count=max(pages),
                    number_prefix='p',
                    ext='.'+typestr)
            imgfullpath = os.path.join(dst_folder, imgfile)
            img.save(filename=imgfullpath)

        fb.close()

    return imgfullpath
