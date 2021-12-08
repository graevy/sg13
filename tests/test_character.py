import pytest
import src

char = src.character.Character.create(dict(name='named', race='human', clas='soldier', level=1))

def test_character_creation():
    assert type(char) == src.character.Character

def test_level_up_auto():
    level_old = char.level
    char.level_up_auto()
    assert char.level - level_old == 1

def test_level_up_auto_stats():
    attrs_old = char.attributes
    skills_old = char.skills
    char.level_up_auto()
    assert char.attributes != attrs_old and char.skills != skills_old
