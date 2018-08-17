# -*- coding: utf-8 -*-
"""Parse documents and store extracted text in a database.

@author: Malte Persike
"""

# Python core modules and packages
import logging, os
from datetime import datetime

# Third party modules and packages
import pytesseract as pt
pt.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

# Local modules and packages
import lib.constants as constants
from lib.db_helper import documentExists, storeDocument
from lib.import_helper import parseLtObjs
from lib.import_conf import DEFAULT_IMPORTOPTIONS, DEFAULT_LOGNAME
from lib.pdfutil import savePDFPageAsImage, DEFAULT_RESOLUTION
from lib.fileutil import collectFiles, divineImagefolder

# Constants and other objects
DEFAULT_OCR_LANGUAGE = 'deu'
DEFAULT_OCR_SAVEEXTENSION = '.txt'
logger = logging.getLogger(DEFAULT_LOGNAME)


def runOCRonPDF(filename, tmp_folder='.', pages=[], filetype='.tif', resolution=DEFAULT_RESOLUTION):
    """Run Tesseract OCR on a given set of pages from a PDF file. Pages are
    first exported to image files, then OCR'ed and finally, the recognized
    text is retrieved.
    
    Args:
        filename(str): PDF file to run OCR on.
        tmp_folder(str, optional): A folder where temporary image files are stored.
        filetype(str, optional): The file type of the temporary image files.
        resolution(int, optional): The resolution of the temporary image files.

    Returns:
        str: the recognized text.
    """
        
    content = ''
    
    imgfullpath = savePDFPageAsImage(
            src_name=filename,
            dst_folder=tmp_folder,
            pages=pages,
            filetype=filetype,
            resolution=resolution)
    
    if imgfullpath:
        if pt.pytesseract.run_tesseract(
                input_filename=imgfullpath,
                output_filename_base=os.path.splitext(imgfullpath)[0],
                extension=DEFAULT_OCR_SAVEEXTENSION.strip('.'),
                lang=DEFAULT_OCR_LANGUAGE):
            txtfullpath = os.path.splitext(imgfullpath)[0] + DEFAULT_OCR_SAVEEXTENSION
            with open(txtfullpath, 'r', encoding="utf8") as fr:
                content = str(fr.read())
            os.remove(txtfullpath)
        os.remove(imgfullpath)
        
    return content


def readFromPDF(filename, db, options=DEFAULT_IMPORTOPTIONS):
    """Extract contents from a PDF file using either text extraction or OCR.
    
    Args:
        filename (str): filename from which to extract content.
        db: a database object.
        options (ImportOptions): tuple holding various settings.

    Returns:
        bool: True if at least one character of text was imported,
            False otherwise.
    """

    # Build identifier record for duplicate checking. This could be user-definable.
    record = {
            'content_name': os.path.basename(filename), 
            'filecreated_date': str(datetime.fromtimestamp(os.stat(filename).st_ctime))
            }

    parsed_ok = False    
    if not documentExists(record, db):
        # Open the given file. The file needs to be kept open as long as calls to
        # PDFParser() are made, hence the rather long file lock period.
        try:
            fp = open(filename, 'rb')
        except IOError as e:
            logger.error(e, exc_info=True)
            fp = None
    
        # Start text extraction
        if fp:
            # Create parser object to parse pdf content
            parser = PDFParser(fp)
    
            # Store the parsed content in PDFDocument object
            document = PDFDocument(parser, '')
    
            # Check if document is extractable, if not abort
            if not document.is_extractable:
                logger.error("Text extraction not allowed in '{0}'.".format(filename))
            	
            # Create PDFResourceManager object that stores shared resources such as fonts or images
            rsrcmgr = PDFResourceManager()
            
            # Set parameters for analysis
            laparams = LAParams()
            
            # Create a PDFDevice object which translates interpreted information into desired format
            # Device needs to be connected to resource manager to store shared resources
            # device = PDFDevice(rsrcmgr)
            # Extract the decive to page aggregator to get LT object elements
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)

            # Create interpreter object to process page content from PDFDocument
            # Interpreter needs to be connected to resource manager for shared resources and device 
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            # We might have to save image files, so get a folder name for them.
            img_folder = divineImagefolder(
                basefolder=options.imageFolder,
                filename=filename,
                as_subfolder=options.createSubfolders,
                create=True)

            # Now that we have everything to process a pdf document, lets process it page by page
            content = ''
            page_hadextractabletext = []
            for page_number, page in enumerate(PDFPage.create_pages(document)):
                logger.info('Extracting text from p. {0}'.format(page_number+1))

                # As the interpreter processes the page stored in PDFDocument object
                interpreter.process_page(page)

                # The device renders the layout from interpreter
                layout = device.get_result()

                # Out of the many LT objects within layout, we are interested in LTTextBox and LTTextLine
                page_text = ''

                # Traverse all objects in the PDF file            
                for lt_obj in layout:
                    page_text+= parseLtObjs(
                            lt_objs=[lt_obj],
                            src_fullpath=filename,
                            page_number=page_number,
                            dst_folder=img_folder,
                            options=options)

                page_hadextractabletext+= [bool(page_text)]

                # No text will be extracted from an image-only page. In such
                # cases, try OCR.
                if not page_hadextractabletext[-1]:
                    logger.info('Page {0} had no extractable text. Trying OCR.'.format(page_number+1))
                    page_text+= runOCRonPDF(
                            filename=filename,
                            tmp_folder=img_folder,
                            pages=[page_number],
                            resolution=options.imageResolution
                            )

                if page_text:
                    content+= '\n' + page_text

            # Store, finally
            parsed_ok = storeDocument(content, '|'.join([['OCR', 'Text'][idx] for idx in set(page_hadextractabletext)]), filename, db)

        fp.close()
    else:
        logger.warning('Possible duplicate database entry found. Content was not stored in database.\nDuplicate information: ' + str(record))

    return parsed_ok


def importFiles(files, db, options=DEFAULT_IMPORTOPTIONS):
    """Iterate through a list of files, extract their content and store those
    in a database.
    
    Args:
        files (list): a list of filenames from which to extract content.
        db: a database object.
        options (ImportOptions): options for importing.
    
    Returns:
        int: the number of imported files
    """

    count_imported = 0
    for f in files:
        ext = os.path.splitext(f)
        if ext and (ext[-1].casefold() in constants.FILEEXT_PDF):
            logger.info("Processing file: '{0}'".format(f))
            count_imported+= readFromPDF(f, db, options)
        else:
            logger.warning("'{0}' files are currently not supported.".format(ext.uppper()))

    return count_imported


def importFolder(folder, db, options=DEFAULT_IMPORTOPTIONS):
    """Iterates through a folder, extracts file content and store those
    in a database.
    
    Args:
        folder (str): a folder containing the files from which to extract content.
        db: a database object.
        options (ImportOptions): options for importing.
            
    Returns:
        int: the number of imported files
    """
    files = collectFiles(folder, '\.pdf$')
    return importFiles(files, db, options)
