# -*- coding: utf-8 -*-
"""Helper functions for text processing.

@author: Malte Persike
"""

# Third party modules and packages
import numpy as np
from PIL import Image
import wordcloud


# Function definitions
def createWordcloud(freqs, fullpath, maskfile, maxwords=100):
    """Create a word cloud from a given dictionary of word frequencies. The
    wordcloud will assume the shape defined by the alpha channel of a given
    maskfile.
    
    Args:
        freqs (dict)): Words and their frequencies.
        fullpath (str): full path and filename for the generated image file.
        maskfile (str): full path and filename of an image file defining the
            shape of the wordcloud. The image must be an RGBA png file, where
            the alpha channel defines the target shape.
        maxwords (int): maximum number of words in the wordcloud.

    Returns:
        None
    """
    mask = np.array(Image.open(maskfile))
    wc = wordcloud.WordCloud(
            background_color='white',
            mask=mask,
            max_words=maxwords,
            )
    wc.generate_from_frequencies(freqs)
    wc.to_file(fullpath)
