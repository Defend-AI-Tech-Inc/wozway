

import importlib.metadata

__title__: str = "defendai-wozway"
__version__: str = "0.0.1"

try:
    if __package__ is not None:
        __version__ = importlib.metadata.version(__package__)
except importlib.metadata.PackageNotFoundError:
    pass
