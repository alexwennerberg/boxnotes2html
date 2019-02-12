from boxnotes2html import BoxNote
from fixtures.notes import *


def test_boxnote_loads(simple_note):
    assert simple_note
    assert simple_note.text
    assert simple_note.attribute_pool


def test_loads_from_file(simple_note_fullpath):
    boxnote = BoxNote.from_file(simple_note_fullpath)
    assert boxnote
    assert str(boxnote)


def test_simple_note_metadata(simple_note):
    # WIP
    assert simple_note.get_metadata()


def test_simple_note_parsing(simple_note):
    return


def test_attribute_chunk(simple_attribute):
    assert simple_attribute
    assert simple_attribute.attributes == set([1, 36, 4])
    assert simple_attribute.num_characters == 3


def test_attributes(simple_note):
    assert simple_note.attribute_chunks


def test_convert_to_html(simple_note):
    print(simple_note.as_html())
    assert simple_note.as_html()


def test_convert_to_html_complex(complex_note):
    print(complex_note.as_html())
    assert complex_note.as_html()
