# -*- coding: utf-8 -*-
"""Functions for processing documents as a bag of words.

@author: Malte Persike
"""

# Python core modulees and packages
import os, re

# Third party modulees and packages
import nltk

# Local modulees and packages
from lib.constants import DEFAULT_COMMENTTOKEN
from lib.import_conf import DEFAULT_IMPORTOPTIONS
from lib.txt_helper import stripChars

# Function definitions
def collectFrequencies(coll, content_field, filter='', options=DEFAULT_IMPORTOPTIONS):
    """Collect word frequencies from a document collection.

    Args:
        coll: a database collection object.
        content_field (str): document field from which to extract the text.
        filter (str): A filter for the selected documents.
        options (ImportOptions): tuple holding various settings.

    Returns:
        dict: Words with their relative frequencies (0...1).
    """

    # Read stopwords from file
    comment_re=re.compile(r'\s*[{0}]'.format(DEFAULT_COMMENTTOKEN))
    stopwords = {line.strip() for line in list(open(os.path.join('.','lib','stopwords_german.txt'), encoding='utf-8')) if not comment_re.match(line)}

    # Retrieve and count
    freqs = dict()
    for doc in coll.find(filter):
        # Get a word list from the content
        text = stripChars(doc[content_field], replacewith=' ')
        text = stripChars(text, stripchars='!„"#$%&\'()*+,-–./:;<=>?@[\\]^_`{|}~1234567890')
        words = nltk.word_tokenize(text)

        # Sanitize word list
        wordmap = map(lambda word: word.casefold() if ((word.casefold() not in stopwords) and (len(word) > 1)) else None, words)
        words = [word for word in wordmap if word is not None]
        
        # Update frequencies
        fdist = nltk.FreqDist(words)
        
        # Normalize frequencies so that each document only contributes a
        # cumulative frequency of 1.0.
        for word in fdist:
            if word in freqs:
                freqs[word]+= fdist.freq(word)
            else:
                freqs[word] = fdist.freq(word)

    return freqs