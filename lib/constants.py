# -*- coding: utf-8 -*-
"""Global types, variables, and constants.

@author: Malte Persike
"""

# Python core modules and packages
import unicodedata

# Enable/disable logging to console
DEFAULT_LOGTOCONSOLE = True
DEFAULT_COMMENTTOKEN = ';'

# File types for importing
FILEEXT_PDF = '.pdf'

# Non-printable characters
CONTROL_CHARS_UNICODE = ''.join(c for c in (chr(i) for i in range(0x110000)) if unicodedata.category(c) in ['Cc', 'C'])
