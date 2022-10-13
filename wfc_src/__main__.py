# Execute with
# $ python -m example_src          (2.7+)
""" Main entry point """

import sys
import wfc_src

if __package__ is None and not hasattr(sys, 'frozen'):
    # direct call of __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

if __name__ == '__main__':
    wfc_src.main()
