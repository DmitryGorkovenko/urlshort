# -*- coding: utf-8 -*-
import os, sys
shorter = os.path.dirname(__file__)
sys.path.insert(0, shorter)
sys.path.insert(1, '/home/g/gatiatag/.local/lib/python2.7/site-packages/')
from rest import app as application
