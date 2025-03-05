#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, re
import bz2
import pickle

__license__ = 'GPL 3'
__copyright__ = '2010,2018, Hiroshi Miura <miurahr@linux.com>'
__docformat__ = 'restructuredtext en'

def o(str):
    try:
        return ord(str.decode("utf-8"))  # Python 2
    except AttributeError:
        return ord(str)  # Python 3

class UnihanConv():

    readings = {}
    firsttime = True
    lang = None
    priority = {
        'kr':  [ 'kKorean', 'kMandarin', 'kJapaneseOn', 'kVietnamese', 'kCantonese', 'kJapaneseKun'],
        'zh': [ 'kMandarin', 'kCantonese', 'kKorean',  'kJapaneseOn', 'kVietnamese', 'kJapaneseKun'],
        'yue': [ 'kCantonese', 'kMandarin', 'kKorean',  'kJapaneseOn', 'kVietnamese', 'kJapaneseKun'],
        'ja': [ 'kJapaneseOn', 'kJapaneseKun', 'kMandarin', 'kCantonese', 'kKorean',  'kVietnamese'],
        'vn': [ 'kVietnamese', 'kMandarin', 'kCantonese', 'kJapaneseOn', 'kJapaneseKun', 'kKorean'],
    }
    pmap = {
        o('â'):'a',o('à'):'a',o('ắ'):'a',o('ă'):'a',o('ấ'):'a',
        o('ü'):'u',o('ụ'):'u',o('ú'):'u',o('ử'):'u',o('ư'):'u',
        o('ù'):'u',
        o('é'):'e',
        o('ọ'):'o',o('ố'):'o',o('ộ'):'o',o('ơ'):'o',o('ớ'):'o',
        o('ớ'):'o',
     }

    def __init__(self, lang):
        if lang in self.priority:
            self.lang = lang
        else:
            self.lang = 'zh'

    def run(self, source, dest):
        max_len = 0
        tbl = {}
        self.process_readings(source, tbl)
        max_len = max(max_len, len(tbl))
        out_fn = dest + '.bz2'
        # Update BZ2File call to use named parameters for Python 3.13 compatibility
        outfile = bz2.BZ2File(out_fn, 'w', compresslevel=9)
        try:
            pickle.dump((tbl, max_len), outfile, protocol=2)
        finally:
            outfile.close()

    def check_category(self, lcode, category, pron):
        try:        
            p = self.priority[self.lang].index(category)
        except:
            return

        if not ((lcode in self.readings) and (self.readings[lcode][1] < p)):
            if category in ['kMandarin', 'kCantonese']:
                self.readings[lcode] = (re.sub(r'(\w+)[1-5]',r'\1 ',pron), p)
            elif category == 'kHanyuPinyin': # pragma: no branch
                self.readings[lcode] = (re.sub(r'\w+\.\w+:(\w+)',r'\1 ',pron), p) # pragma: no cover
            else:
                self.readings[lcode] = ("%s "%pron, p)

    def gen_map(self, tbl, ucode):
        # Fix the 'is 0' comparison to '== 0'
        if ucode == 0:
            return

        tmap = []
        for i in range(0, 256):
            if i in self.readings:
                reading = self.readings[i][0]
                if all(ord(c) < 128 for c in reading):
                    tmap.append(reading)
                else:
                    tmap.append(reading.encode("utf-8")) # pragma: no cover
            else:
                tmap.append('')
        tbl['x%x'%ucode] = tmap

    def process_readings(self, source, tbl): # pragma: no cover
        try:
            with open(source, 'r', encoding='utf8') as f: #python3
                self.process_file(f, tbl)
        except:
            with open(source, 'r') as f: #python2
                self.process_file(f, tbl)

    def process_file(self, f, tbl):
        oucode = 0

        r1 = re.compile(r'U\+([0-9A-F]{2,3})([0-9A-F]{2}\b)')
        for line in f:
            items = line[:-1].split('\t')

            try:
                code = r1.sub(r'\1\t\2',items[0]).split('\t')
                category = items[1]
                ptmp = items[2].split(' ')[0].capitalize()
                pron = re.sub('[^\00-\x7f]', lambda x: self.pmap[ord(x.group())], ptmp) 
            except:
                continue

            if code is None:
                continue # pragma: no cover

            ucode = int(code[0],16)
            lcode = int(code[1],16)
            if (oucode != ucode):
                self.gen_map(tbl, oucode)
                oucode = ucode 
                self.readings={}
            self.check_category(lcode, category, pron)

        self.gen_map(tbl, oucode) # output when eof

