"""
The primary module for processing and parsing Box Notes
"""
import json
import os
import re
from functools import reduce
from xml.etree import ElementTree as ET

import typing

from . import html, markdown
from .table import Table

dir_path = os.path.dirname(os.path.realpath(__file__))


class AttributeChunk:  # not really a class
    """
    An attribute chunk is formatted like this:
    *n[*n...]+n[|n+n]
    eg
    *4*1+1|+1
    where *n refers to an attribute to apply from the attribute pool
    and +n is a number of characters to apply that attribute to
    and |n is indicative of a line break (unclear the purpose of this)
    """

    def __init__(self, attribute_string_chunk, position=None):
        self.attribute_string_chunk = attribute_string_chunk
        self.attributes = set(self._all_items_after_indicator("*"))
        self.num_characters = sum(self._all_items_after_indicator("+"))
        self.num_linebreaks = sum(self._all_items_after_indicator("|"))

    def _all_items_after_indicator(self, indicator):
        """
        Regex to get all the numbers after the given indicator
        Then convert this base36 number into an integer
        * -> attribute
        + -> number of characters to apply attribute to
        | -> number of linebreaks (I think)
        """
        items = re.findall(
            "\\{}([^\\+\\|\\*]*)".format(indicator), self.attribute_string_chunk
        )
        return map(lambda x: int(x, 36), items)


class FormattedText:
    """
    A block of text with parsed information about it
    """

    def __init__(self, attributes, text, num_linebreaks, tagnums=None):
        self.attributes = attributes
        self.tagnums = list(tagnums)  # for debugging
        self.styles = self.get_base_styles()
        self.num_linebreaks = num_linebreaks
        self.text = text
        self.element_tree = self.styles_to_elements()
        self.table_id, self.row_id, self.column_id = self.get_table_info()
        self.list_type, self.list_level = self.get_list_info()
        return

    def get_base_styles(self):
        tags = []
        for attribute in self.attributes:
            tags.append(html.convert_simple_element_to_html_tag(attribute))
        if not tags:
            tags = html.HTMLTag("span", {})  # hmm
        return tags

    def get_table_info(self):
        table_id = row_id = column_id = None
        for box_attribute in self.attributes:
            if html.get_table_info(box_attribute)[0]:
                table = html.get_table_info(box_attribute)
                if table_id and table[0] != table_id:
                    raise NotImplementedError(f"Encountered table id {table[0]} but was expecting {table_id}")

                table_id = table[0]
                if table[1]:
                    row_id = table[1]
                if table[2]:
                    column_id = table[2]
        return table_id, row_id, column_id

    def get_list_info(self):  # refactor
        for box_attribute in self.attributes:
            if html.get_list_info(box_attribute):
                return html.get_list_info(box_attribute)
        return None, None

    def styles_to_elements(self):
        if self.text.replace("\n", "") == "*":  # maybe change
            self.text = ""

        # LISTS HACK -- After much anguish, I have resorted myself to the dark arts
        # Please forgive me
        # We are using <li/> to represent list items
        if "li" in [a.tag for a in self.styles]:
            span = ET.Element("span")
            indent_level = self.get_list_info()[1] - 1 or 0
            span.text = indent_level * "&nbsp;&nbsp;" + "* "
            return span

        def _append(x, y):
            y.append(x)
            return y

        individual_elements = list(
            map(lambda x: ET.Element(x.tag, x.attributes), self.styles)
        )
        reduce(_append, individual_elements)
        lowest_element = individual_elements[0]  # indexerror
        toplevel_element = individual_elements[-1]
        for _ in range(self.num_linebreaks):
            toplevel_element.append(ET.Element("br"))  # Hm
        lowest_element.text = self.text
        return toplevel_element

    def styles_to_markdown_string(self):
        # escape markdown characters
        # kind of awkward
        characters_to_escape = "\\*[]`"
        tmp = self.text or ""
        out_text = ""
        if tmp is not None:
            for character in characters_to_escape:
                tmp = tmp.replace(character, "\\{}".format(character))
            for line in tmp.split("\n"):
                _prefix = ""
                
                for box_attribute in self.attributes:
                    if line or box_attribute[0] in ["list", "image", "link"]:
                        start, end, prefix = markdown.convert_simple_element_to_markdown(
                            box_attribute
                        )
                        if prefix:
                            # Hacky solution to ensure headers always appear at the start of the line
                            _prefix += start
                            line = line + end
                        else:
                            line = start + line + end
                            
                out_text += _prefix + line
            out_text += "\n" * (self.num_linebreaks)

        return out_text

    def __repr__(self):
        return json.dumps(
            {k: v for k, v in self.__dict__.items() if k != "element_tree"}, indent=2
        )


class BoxNote:
    NOTE_MAPPING = []  # MAPPING FROM ATTRIB TO HTML TAG

    def __init__(self, note_string):  # TODO: rename notefile to notefilepath
        """
        note_string: the note data as a string
        text is the raw text of the notes document.
        attributes is the attribute formatting string
        attribute pool is all the attributes that are used and a conversion from
        numattribute number to some html-like formatting
        """
        self.note_data = json.loads(note_string)
        self.text = self.note_data["atext"]["text"]
        self.attribute_chunks = self._attribute_chunks_from_string(
            self.note_data["atext"]["attribs"]
        )
        self.attribute_pool = self.note_data["pool"]["numToAttrib"]
        # config?

    @classmethod
    def from_file(cls, filepath):
        with open(filepath, encoding="utf8") as f:
            return cls(note_string=f.read())

    def get_metadata(self):
        """
        returns potentially useful metadata about the file. ignores more obscure
        metadata that is mostly for internal user. WIP, currently unused
        """
        metadata = {"last_edit_timestamp": self.note_data.get("lastEditTimestamp")}
        return metadata

    @staticmethod
    def _attribute_chunks_from_string(attributes_string):
        return map(AttributeChunk, re.findall("\\*.*?\\+[^\\*]*", attributes_string))

    def _get_formatted_text_list(self):
        text = self.text
        output = []
        pointer = 0
        for chunk in self.attribute_chunks:
            attributes = [
                self.attribute_pool[str(attribute_number)]
                for attribute_number in chunk.attributes
            ]
            element_text = text[pointer : pointer + chunk.num_characters]
            blob = FormattedText(
                attributes, element_text, chunk.num_linebreaks, tagnums=chunk.attributes
            )
            output.append(blob)
            pointer += chunk.num_characters
        return output

    def as_element_tree(self):
        html_result = ET.Element("html")
        body = ET.SubElement(html_result, "body")
        blobs = self._get_formatted_text_list()
        for blob in blobs:
            body.append(blob.element_tree)
        return html_result

    def as_html(self):
        with open(os.path.join(dir_path, "style.css")) as f:
            css = "<style>" + f.read() + "</style>"
        body = ET.tostring(self.as_element_tree(), encoding="unicode").replace(
            "&amp;nbsp;", "&nbsp;"
        )
        return css + body

    def as_markdown(self):
        """
        Return this note as markdown.
        
        ## Notes about tables
        
        1. A new row starts with start with `struct-table[hash]_col[hash]` and then `struct-table[hash]_row[hash]`.
        2. The continuation of a row can be identified by `struct-table[hash]_row[hash]` and then `struct-table[hash]_col[hash]`
        3. The FormattedText that appears directly before a `struct-table[hash]_col|row[hash]` contains the content for
           the cell.
        4. There doesn't appear to be an indication of a header row
        5. There can be multiple blobs of data before the `struct-table[hash]_col|row[hash]` and therefore you need to
           capture this data so that it can be inserted into a table cell.
        6. BUT... there doesn't seem to be any indication that a table has finished. In some cases the last table cell
           will contain a \n\n but not always.
           Thus, this is why in this method we add the data to the stack, but then if we detect there is a table cell
           that hasn't been filled, we fill it with any data since the previously encountered table cell.
        """
        
        #: A dict of data that makes up the box note.
        #
        # The key will either be;
        #     1. An integer derived from the index of blobs; or
        #     2. A string that references a table_id derived from the Box Note attribute
        #        `struct-table[table-id]_col|row[hash]`
        out: typing.Dict[typing.Union[int, str], typing.Union[str, Table]] = {}
        
        #: A list of blob indexes that are captured so they can be placed within a table cell upon discovery.
        captures: typing.List[int] = []
        
        blobs = self._get_formatted_text_list()
        
        for i, blob in enumerate(blobs):
            if blob.table_id:
                # This blob contains reference to a table
                #
                # Some previously captured data forms the data that will be placed within this particular table cell.
                
                if blob.table_id not in out:
                    # This is the first time we've come across this table, so creat an instance of Table in which
                    # we can start to place data in.
                    out[blob.table_id] = Table()
                
                # Combine any text previously captured together.
                data = ''.join([
                    out.pop(capture)
                    for capture in captures
                ])
                
                if len(data) > 0:
                    # Add the previously captured data to the table
                    #
                    # Table relies on a dictionary (which now honours the insertion order) to ensure that this data
                    # will be in the correct row/column and that that row/column is rendered in the correct place
                    # on output.
                    out[blob.table_id].add_data(blob.row_id, blob.column_id, data)

                captures = []

            else:
                if blob.num_linebreaks == 0:
                    # Capture a reference to this data in case it needs to be placed inside a table cell
                    captures.append(i)
                else:
                    # We reset the capture when there is a line break.
                    captures = []

                out[i] = blob.styles_to_markdown_string()

        doc = ''.join([
            o.render_markdown() if hasattr(o, "render_markdown") else o
            for o in out.values()
        ])
        
        # TODO: Better support for cleaning up the doc
        cleanup = (
            # Box Notes can give you text in a table cell like `**H****ello**` - this is invalid Markdown and we want
            # to convert it to `**Hello**`.
            ('****', ''),
        )
        
        for search, replace in cleanup:
            doc = doc.replace(search, replace)
            
        return doc

    def as_text(self):
        return self.text

    def __str__(self):
        return json.dumps(self.note_data, indent=2)
