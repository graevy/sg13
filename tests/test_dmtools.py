import pytest
import src
import functools

import random
from statistics import NormalDist
from copy import deepcopy
import json
import os
import rolls


FACTIONS = src.dmtools.load()
CHARACTERS = src.dmtools.get_chars(factions)

# TODO P3: create tests don't simulate user input at all. needs partial function injection via functools module
def test_create_basic():
    kwargs = dict(name='test', race='human', class_='scientist', faction='sgc', level=1)
    char = src.dmtools.create(mode=0, **kwargs)
    for k,v in kwargs.items():
        assert char.__dict__[k] == v

def test_create_mode_1():
    kwargs = dict(name='test', race='human', class_='scientist', faction='sgc', level=1,
        attributes={'strength':15}, skills={'anthropology':4})
    char = src.dmtools.create(mode=1, **kwargs)
    for k,v in kwargs.items():
        assert char.__dict__[k] == v


def test_load():
    assert FACTIONS and type(FACTIONS) == dict

def test_get_chars():
    assert CHARACTERS and type(CHARACTERS[0]) == src.character.Character

