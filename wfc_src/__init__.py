""" Init """
import sys
import os

from wfc_src.wfc import WFC

def _real_main(argv=None):
    ''' Real main function.'''
    #print('__init__._real_main()')

    # get the path + filename
    # Example: C:\Users\...\RubikQuat\rubikquat_src\__init__.pyc
    path = os.path.realpath(os.path.abspath(__file__))
    # remove filename (leave only path)
    # Example: C:\Users\...\RubikQuat\rubikquat_src
    path = os.path.dirname(path)

    # if frozen (py2exe generated exe) remove the 'rubikquat.exe'
    # from: C:\Users\...\RubikQuat\build\rubikquat.exe\rubikquat_src
    #   to: C:\Users\...\RubikQuat\build\
    if hasattr(sys, 'frozen'):
        path = os.path.dirname(path)
        path = os.path.dirname(path)

    wfc = WFC(768, 768, path)
    #wfc = WFC(2000, 2000, path)
    wfc.run()

    retcode = 0
    sys.exit(retcode)


def main(argv=None):
    ''' Main '''
    #print('__init__.main()')
    _real_main(argv)
