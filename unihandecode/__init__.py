# -*- coding: utf-8 -*-

__license__ = 'GPL 3'
__copyright__ = '2010-2018, Hiroshi Miura <miurahr@linux.com>'
__docformat__ = 'restructuredtext en'
__all__ = ["Unihandecoder"]

'''
Decode unicode text to an ASCII representation of the text. 
Translate unicode characters to ASCII.

inspired from John's unidecode library.
Copyright(c) 2009, John Schember

Tranliterate the string from unicode characters to ASCII in Chinese and others.

'''
import unicodedata
import importlib

# Use lazy imports to avoid loading modules during package installation
def _import_decoder(name):
    module_name = f"unihandecode.{name}"
    module = importlib.import_module(module_name)
    return getattr(module, name.capitalize() + "decoder")

class Unihandecoder(object):
    preferred_encoding = None
    decoder = None

    def __init__(self, lang="zh", encoding='utf-8'):
        self.preferred_encoding = encoding
        if lang == "ja":
            Jadecoder = _import_decoder("ja")
            self.decoder = Jadecoder()
        elif lang == "kr":
            Krdecoder = _import_decoder("kr")
            self.decoder = Krdecoder()
        elif lang == "vn":
            Vndecoder = _import_decoder("vn")
            self.decoder = Vndecoder()
        else: # zh and others
            from unihandecode.unidecoder import Unidecoder
            self.decoder = Unidecoder(lang)

    def _text_filter(self, text):
        # at first unicode normalize it. (see Unicode standards)
        return unicodedata.normalize('NFC', text)

    def decode(self, text):
        return self.decoder.decode(self._text_filter(text))

_unidecoder = None

def unidecode(text):
    '''
    backword compatibility to unidecode
    '''
    global _unidecoder
    if _unidecoder == None:
        _unidecoder = Unihandecoder()
    return _unidecoder.decode(text)
