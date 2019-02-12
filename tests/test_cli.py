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
