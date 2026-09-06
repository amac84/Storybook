import os
import pathlib
import tempfile
import unittest
import sys

ROOT = pathlib.Path(__file__).resolve().parent / 'source'
TEMP = pathlib.Path(__file__).resolve().parent
native_mkdir = os.mkdir

def compatible_mkdir(path, mode=0o777, *, dir_fd=None):
    resolved = pathlib.Path(path).resolve()
    if mode == 0o700 and resolved.is_relative_to(TEMP):
        mode = 0o777
    return native_mkdir(path, mode, dir_fd=dir_fd)

os.mkdir = compatible_mkdir
tempfile.tempdir = str(TEMP)
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT / 'tests')))
sys.exit(0 if result.wasSuccessful() else 1)
