from setuptools import setup

setup (
   name = 'restruct_data',
   version = '1.0',
   author = 'Sofia Assis',
   url  = 'https://github.com/ninja-asa',
   packages = ['restructIMARIS'],
   setup_requires=['wheel'],
   install_requires = [
       'wheel',
       'pandas',
       'seaborn',
       'easygui',
       'openpyxl',
       'xlrd'
   ]
)