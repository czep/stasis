import pathlib
import shutil
import importlib.resources
from distutils.dir_util import copy_tree

from .config import *

def init(args, conf):

    print("Initializing new static site...")
    print("Target directory: {}".format(pathlib.Path('.').resolve()))

    # do not continue unless current directory is empty
    if any(pathlib.Path('.').iterdir()):
        print("Ensure target directory is empty before initializing!")
        return

    bootstrap_path = pathlib.Path(__file__).parent / BOOTSTRAP_PATH
    copy_tree(bootstrap_path.resolve(), str(pathlib.Path('.').resolve()))

