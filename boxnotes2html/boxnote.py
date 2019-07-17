from functools import reduce
import json
import re
from . import html, markdown
from xml.etree import ElementTree as ET
import os

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
        for box_attribute in self.attributes:
            if html.get_table_info(box_attribute)[0]:
                return html.get_table_info(box_attribute)
        return None, None, None

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
                for box_attribute in self.attributes:
                    if line or box_attribute[0] in ["list", "image", "link"]:
                        start, end = markdown.convert_simple_element_to_markdown(
                            box_attribute
                        )
                        line = start + line + end
                out_text += line
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
        table = ET.Element("table")  # only one for now WIP
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
        out = ""
        blobs = self._get_formatted_text_list()
        for blob in blobs:
            out += blob.styles_to_markdown_string()
        return out

    def as_text(self):
        return self.text

    def __str__(self):
        return json.dumps(self.note_data, indent=2)
