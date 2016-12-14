import sys
import os
shorter = os.path.dirname(__file__)
if not shorter in sys.path:
	sys.path.insert(0, shorter)
from main import app as application
