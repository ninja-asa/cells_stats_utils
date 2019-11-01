from setuptools import setup

setup (
   name = 'restruct_data',
   version = '1.0',
   py_modules = ['restruct_data'],
   author = 'Sofia Assis',
   url  = 'https://github.com/ninja-asa',
   package = ['restructIMARIS'],
   install_requires = [
       'pandas',
       'seaborn',
       'easygui',
       'openpyxl',
       'xlrd'
   ]
)