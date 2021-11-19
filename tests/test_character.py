import pytest
import src

def test_character_creation():
    char = src.character.Character.create(dict(name='named', race='human', clas='soldier', level=1))
    assert type(char) == src.character.Character