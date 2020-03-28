@echo off

py

import sys, os, importlib
sys.path.insert(0, "c:/py/_projects/dnd")
import item, resources, character, dmfunctions
from resources import *
from dmfunctions import *

factions = load()
