import sys
import os

# ADK loads this package from the project root, so bare imports like
# `from shared.consts import` and `import prompt` would fail without this.
# Adding the package directory ensures all internal modules resolve correctly.
sys.path.insert(0, os.path.dirname(__file__))
