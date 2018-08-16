# -*- coding: utf-8 -*-
"""Parse documents and store them in a database.

@author: Malte Persike
"""

# Python core modules and packages
import io, logging, os
from datetime import datetime
# Third party modules and packages
import PyPDF2
import pytesseract as pt
from wand.image import Image
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
# Local modules and packages
import lib.constants as constants
from lib.import_helper import divine_imagefile, divine_imagefolder, parse_lt_objs
from lib.import_conf import DEFAULT_IMPORTOPTIONS, DEFAULT_LOGNAME

# Constants and other objects
logger = logging.getLogger(DEFAULT_LOGNAME)
pt.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

# Function definitions
def documentExists(record, db):
    """Test if a document with a given set of identifiers exists in the database.

    Args:
        record (dict): a dictionary defining the document to be matched.
        db: a database object

    Returns:
        bool: True if document exists, False otherwise
    """
    
    cursor = db.find(record)
    if cursor:
        return cursor.limit(1).count()
    else:
        return False

def savePDFPageAsImage(filename, pages, filetype, options=DEFAULT_IMPORTOPTIONS):
    """Load a PDF file and save the given pages to image files.
    
    Args:
        filename (str): name of the PDF file.
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
        fb = open(filename, "rb")
    except IOError as e:
        logger.error(e)
    else:
        # File opened ok. Let's save them pages
        src_pdf = PyPDF2.PdfFileReader(fb, strict = False)
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
            img = Image(file = pdf_bytes, resolution = options.imageResolution)
            img.type = 'grayscale'
            img.gaussian_blur(radius=3, sigma=1)
            img.compression = 'losslessjpeg'
            img.convert(typestr)
            
            # Divine a file name, verify folder, and save the image
            imgfolder = divine_imagefolder(filename, options, create=True)
            imgfile = divine_imagefile(filename, number=page, count=max(pages), number_prefix='p', ext='.'+typestr)
            imgfullpath = os.path.join(imgfolder, imgfile)
            img.save(filename=imgfullpath)

        fb.close()

    return imgfullpath

def storeDocument(content, source, filename, db):
    """Store a record in the database.
    
    Args:
        content (str): body of data to be stored.
        source (str): information about the content source
        filename (str): full path to the PDF file.
        db: a database object.

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
    
    record = {key: document[key] for key in ['content_name', 'filecreated_date']}
    
    # Check if record exists and store if not.
    stored = False
    if db.find_one(record):
        logger.warning('Possible duplicate database entry found. Content was not stored in database.\nDuplicate information: ' + record)
    elif content:
        stored = db.insert_one(document).acknowledged   # This needs work. There should be checks to not import duplicates.
        logger.info("Content for file {0} stored in database.".format(filename))

    return stored

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

    parsed_ok = False    
    record = {'content_name': os.path.basename(filename), 'filecreated_date': str(datetime.fromtimestamp(os.stat(filename).st_ctime))}
    if not documentExists(record, db):
        # Open the given file. The file needs to be kept open as long as calls to
        # PDFParser() are made, hence the rather long file lock period.
        try:
            fp = open(filename, 'rb')
        except IOError as e:
            logger.error(e, exc_info=True)
            fp = None
    
        # Now, start text extraction
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
            
            # set parameters for analysis
            laparams = LAParams()
            
            # Create a PDFDevice object which translates interpreted information into desired format
            # Device needs to be connected to resource manager to store shared resources
            # device = PDFDevice(rsrcmgr)
            # Extract the decive to page aggregator to get LT object elements
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)

            # Create interpreter object to process page content from PDFDocument
            # Interpreter needs to be connected to resource manager for shared resources and device 
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            # Ok now that we have everything to process a pdf document, lets process it page by page
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
                    page_text+= parse_lt_objs([lt_obj], filename, page_number, options, [])

                page_hadextractabletext+= [bool(page_text)]

                # No text will be extracted from an image-only page. In such
                # cases, try OCR.
                if not page_hadextractabletext[-1]:
                    logger.info('Page {0} had no extractable text. Trying OCR.'.format(page_number+1))
                    imgfullpath = savePDFPageAsImage(filename, page_number, '.tif')
                    if imgfullpath:
                        if pt.pytesseract.run_tesseract(imgfullpath, os.path.splitext(imgfullpath)[0], extension='txt', lang='deu'):
                            txtfullpath = os.path.splitext(imgfullpath)[0]+'.txt'
                            with open(txtfullpath, 'r', encoding="utf8") as fr:
                                page_text = str(fr.read())
                            os.remove(txtfullpath)
                        os.remove(imgfullpath)

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
