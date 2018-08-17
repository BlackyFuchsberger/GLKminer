# -*- coding: utf-8 -*-
"""Helper functions for text processing.

@author: Malte Persike
"""

# Python core modules and packages
import unicodedata, re

# Constants and other objects
CONTROL_CHARS_UNICODE = ''.join(c for c in (chr(i) for i in range(0x110000)) if unicodedata.category(c) in ['Cc', 'C'])


# Function definitions
def stripChars(text, stripchars=CONTROL_CHARS_UNICODE, replacewith=''):
    control_char_re = re.compile('[{0}]+'.format(re.escape(stripchars)))

    return control_char_re.sub(replacewith, text)
