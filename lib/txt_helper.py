# -*- coding: utf-8 -*-
"""Helper functions for text processing.

@author: Malte Persike
"""

# Python core modules and packages
import re

# Local modules and packages
from lib.constants import CONTROL_CHARS_UNICODE


# Function definitions
def stripChars(text, stripchars=CONTROL_CHARS_UNICODE, replacewith=''):
    """Replace a set of characters in a string with a single replacement token.
    If no set of characters is given, all non-printable characters will be
    replaced. If no replacement token is given, the set of characters will be
    removed from the string.
    
    Args:
        text (str): the string on which to perform search-and-replace.
        stripchars (str): list of characters to replace or remove.
        replacewithh (str): string to replace the set of characters with.

    Returns:
        str: the resulting string.
    """

    control_char_re = re.compile('[{0}]+'.format(re.escape(stripchars)))

    return control_char_re.sub(replacewith, text)
