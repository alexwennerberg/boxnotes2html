from unittest.mock import patch

from boxnotes2html import cli


@patch("boxnotes2html.cli.write_file")
def test_command_line_runs(write_file):
    args = ["a", "b", "-f", "md"]
    cli.run_with_args(args)
    assert write_file.call_count == 2


def test_everything():
    for txtfmt in "md", "txt", "html":
        args = ["tests/fixtures", "-f", txtfmt]
        cli.run_with_args(args)


def test_table_simple():
    args = ["tests/fixtures/table-simple.boxnote", "-f", "md"]
    cli.run_with_args(args)


def test_table_multiline():
    args = ["tests/fixtures/table-multiline.boxnote", "-f", "md"]
    cli.run_with_args(args)
    

def test_table_aligned():
    args = ["tests/fixtures/table-aligned.boxnote", "-f", "md"]
    cli.run_with_args(args)


def test_same_line_formatting():
    args = ["tests/fixtures/same-line-formatting.boxnote", "-f", "md"]
    cli.run_with_args(args)
