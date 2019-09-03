"""
Command line interface for boxnotes2html
"""
import argparse
import os
import sys

from boxnotes2html.boxnote import BoxNote


def run():
    run_with_args(sys.argv[1:])


def run_with_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "files",
        help="file or files to process. If passed a directory, will process everything in that directory with the .boxnote extension.",
        nargs="*",
    )
    # TODO: implement
    parser.add_argument(
        "-r", "--recurse", help="recursively look through a folder", action="store_true"
    )
    parser.add_argument(
        "-f",
        "--filetype",
        help="output filetype: markdown or html or plaintext. Default html",
        choices=["md", "html", "txt"],
        default="html",
    )
    args = parser.parse_args(args)

    for filepath in args.files:
        if os.path.isdir(filepath):
            for root, dirs, files in os.walk(filepath):
                for subfile in files:
                    full_path = os.path.join(root, subfile)
                    if full_path.endswith(".boxnote"):
                        write_file(full_path, args.filetype)
        else:
            write_file(filepath, args.filetype)


def write_file(filepath, filetype):
    note = BoxNote.from_file(filepath)
    if filetype == "html":
        out_string = note.as_html()
    elif filetype == "md":
        out_string = note.as_markdown()
    elif filetype == "txt":
        out_string = note.as_text()
    output_path = os.path.splitext(filepath)[0] + ".{}".format(filetype)
    print("writing file {}".format(output_path))
    with open(output_path, "w") as f:
        f.write(out_string)
