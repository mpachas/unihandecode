# coding:utf8
__license__ = 'GPL 3'
__copyright__ = '2010-2018, Hiroshi Miura <miurahr@linux.com>'
__docformat__ = 'restructuredtext en'

'''
Decode unicode text to an ASCII representation of the text for Japanese.
 Translate unicode string to ASCII roman string.

API is based on the python unidecode,
which is based on Ruby gem (http://rubyforge.org/projects/unidecode/) 
and  perl module Text::Unidecode
(http://search.cpan.org/~sburke/Text-Unidecode-0.04/). 

This functionality is owned by Kakasi Japanese processing engine.

Copyright (c) 2010,2015,2018 Hiroshi Miura
'''

import os, re

from unihandecode.unidecoder import Unidecoder

# Defer pykakasi import to runtime when actually needed
pykakasi_available = None
kakasi = None

def _load_pykakasi():
    global pykakasi_available, kakasi
    try:
        import pykakasi
        pykakasi_available = True
        kakasi = pykakasi.kakasi()
        kakasi.setMode("J", "a")
        kakasi.setMode("E", "a")
        kakasi.setMode("H", "a")
        kakasi.setMode("K", "a")
        kakasi.setMode("s", True)
        kakasi.setMode("C", True)
        return kakasi.getConverter()
    except ImportError:
        pykakasi_available = False
        return None

class Jadecoder(Unidecoder):
    codepoints = {}
    conv = None

    def __init__(self):
        self._load_codepoints('ja')
        self.conv = _load_pykakasi()

    def decode(self, text):
        if self.conv:
            result = self.conv.do(text)
            return re.sub('[^\x00-\x7f]', lambda x: self.replace_point(x.group()), result)
        else:
            return super().decode(text)

