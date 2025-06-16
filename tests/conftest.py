# tests/conftest.py

import sys
import os

# Ajoute src/ au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
