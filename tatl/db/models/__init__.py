from peewee import Model

from os.path import dirname, basename, isfile, join, splitext

import importlib
import glob
import inspect
import sys

all_models = []

_modules = glob.glob(join(dirname(__file__), "*.py"))
_files = [
    splitext(basename(f))[0] for f in _modules if isfile(f) and not f.endswith("__init__.py")
]

_submodules = inspect.getmembers(sys.modules[__name__], inspect.ismodule)
_current_module = sys.modules[__name__]

for module_name in _files:
    module = importlib.import_module(f".{module_name}", package="tatl.db.models")

    for name, cls in inspect.getmembers(module, inspect.isclass):
        # Ignore unwanted classes and our abstract members
        if not issubclass(cls, Model) or name in ["BaseModel", "Model"]:
            continue

        all_models.append(cls)
        setattr(_current_module, name, cls)
