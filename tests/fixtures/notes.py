import os

import pytest

from boxnotes2html.boxnote import AttributeChunk, BoxNote

here = os.path.dirname(__file__)
simple_note_path = "simple_note.boxnote"
complex_note_path = "complex_note.boxnote"


@pytest.fixture
def simple_note_fullpath():
    return os.path.join(here, simple_note_path)


@pytest.fixture
def simple_note():
    '''
    A basic note to test loading/unloading/parsing
    '''
    with open(os.path.join(here, simple_note_path)) as f:
        return BoxNote(f.read())


@pytest.fixture
def complex_note():
    '''
    A more complex, contrived note that has every possible data structure I can think of
    in boxnotes
    '''
    with open(os.path.join(here, complex_note_path)) as f:
        return BoxNote(f.read())


@pytest.fixture()
def simple_attribute():
    return AttributeChunk("*1*4*10+2|1+1")
