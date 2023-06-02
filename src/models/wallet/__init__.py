"""
@author: Arno
@created: 2023-05-29
@modified: 2023-05-29

Allow importing all files in folder
From: https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder

"""
import glob
from os.path import basename, dirname, isfile, join

modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [
    basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")
]
