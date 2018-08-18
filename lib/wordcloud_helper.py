# -*- coding: utf-8 -*-
"""Helper functions for text processing.

@author: Malte Persike
"""

# Python core modules and packages
import os, re

# Third party modules and packages
import numpy as np
import nltk
from PIL import Image
import wordcloud

# Local modules and packages
from lib.import_conf import DEFAULT_IMPORTOPTIONS
from lib.txt_helper import stripChars

# Constants and other variables
DEFAULT_COMMENTTOKEN = ';'

# Function definitions
def createWordcloud(filename, maskfile, coll, filter='', content_field='content', options=DEFAULT_IMPORTOPTIONS):
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

    mask = np.array(Image.open(maskfile))
    wc = wordcloud.WordCloud(
            background_color='white',
            mask=mask,
            max_words=100,
            )
    wc.generate_from_frequencies(freqs)
    wc.to_file(filename)
