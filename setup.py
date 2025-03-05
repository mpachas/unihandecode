#!/usr/bin/python
# derivered from unidecode setup.py

from setuptools import Command, setup, find_packages
from setuptools.command.install import install
from distutils.command.build import build

import os,threading
import sys
import shutil
import importlib.util
import importlib.machinery

# Don't import from the package itself during build
# This allows us to install dependencies first
SUPPORTED_LANG=['kr','ja','zh','vn','yue']

def import_module_from_path(module_name, file_path):
    """Import a module from file path without importing the whole package."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def gen_map():
    # Import directly from file path instead of package
    unihan_conv = import_module_from_path(
        "unihan_conv", 
        os.path.join('unihandecode', 'gencodemap', 'unihan_conv.py')
    )
    unihan_source = os.path.join('unihandecode','data','Unihan_Readings.txt')
    for lang in SUPPORTED_LANG:
        dest = os.path.join('unihandecode',lang+'codepoints.pickle')
        u = unihan_conv.UnihanConv(lang)
        u.run(source = unihan_source, dest=dest)

def catdict(src_a, dst):
    outdict = open(dst,'wb')
    for src_f in src_a:
      shutil.copyfileobj(open(os.path.join('unihandecode','data',src_f),'rb'), outdict)
    outdict.close()

def pre_build():
    # Import directly from file path instead of package
    unicodepoints = import_module_from_path(
        "unicodepoints", 
        os.path.join('unihandecode', 'gencodemap', 'unicodepoints.py')
    )
    u = unicodepoints.Unicodepoints()
    u.run(os.path.join('unihandecode','unicodepoints.pickle'))
    gen_map()

class my_build(build):
    def run(self):
        self.execute(pre_build, (),
                    msg="Running pre build task")
        build.run(self)

class my_install(install):
    def run(self):
        self.execute(pre_build, (),
                    msg="Running pre build task")
        install.run(self) # run normal build command

tests_require = ['nose','coverage','mock']

setup(name='Unihandecode',
      version='0.81',
      description='US-ASCII transliterations of Unicode text',
      url='https://github.com/miurahr/unihandecode/',
      license='GPLv3/Perl',
      long_description="""
It often happens that you have non-Roman text data in Unicode, but
you can't display it -- usually because you're trying to show it
to a user via an application that doesn't support Unicode, or
because the fonts you need aren't accessible. You could represent
the Unicode characters as "???????" or "\15BA\15A0\1610...", but
that's nearly useless to the user who actually wants to read what
the text says.

What Unihandecode provides is a function, 'decode(...)' that
takes Unihancode data and tries to represent it in ASCII characters 
(i.e., the universally displayable characters between 0x00 and 0x7F). 
The representation is almost always an attempt at transliteration 
-- i.e., conveying, in Roman letters, the pronunciation expressed by 
the text in some other writing system.

For example;
>>>d = Unidecoder()
>>>d.decode(u"\u5317\u4EB0")
'Bei Jing'.
d = Unidecoder(lang='ja')
>>>d.decode(u"\u5317\u4EB0")
'Pe King'
      """,
      author='Hioshi Miura',
      author_email='miurahr@linux.com',
      packages = ['unihandecode',
                  'unihandecode.gencodemap'],
      include_package_data = True,
      package_data = {'unihandecode':  ['*.pickle.bz2']},
      provides = [ 'unihandecode' ],
      install_requires = [ 'pykakasi;python_version>="3.5"', 'importlib-resources;python_version<"3.9"' ],
      setup_requires = [],
      test_suite = 'nose.collector',
      tests_require = tests_require,
      cmdclass = {
          'build': my_build
      }
)
