import os
import sys


CURRENT_DIR = os.path.dirname(__file__)
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if BACKEND_DIR not in sys.path:
	sys.path.insert(0, BACKEND_DIR)

from app.main import app

