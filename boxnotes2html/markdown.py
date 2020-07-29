"""
Tools for converting Box Notes to Markdown
"""
from . import html


def convert_simple_element_to_markdown(box_attribute: (str, str)) -> (str, str, bool):
    """
    Return the starting and ending markdown that should appear around some text.
    
    :param box_attribute: Tuple containing the attribute_type and attribute_value.
    :return: A tuple containing the start, end and a boolean value that defines whether this particular start should
             take precedence and be prefixed at the start of the line.
    """
    attribute_type = box_attribute[0]
    attribute_value = box_attribute[1]
    start = ""
    end = ""
    # If True then it signifies that this value should appear at the start of the line.
    prefix = None
    
    if not attribute_type:
        start = end = ""
    elif attribute_type == "bold":
        start = end = "**"
    elif attribute_type == "italic":
        start = end = "*"
    elif attribute_type == "underline":
        start = "<ins>"
        end = "</ins>"
    elif attribute_type == "strikethrough":
        start = end = "~~"
    elif "font-size" in attribute_type:
        sizemap = {"small": "", "medium": "", "large": "## ", "verylarge": "# "}
        size = attribute_type.split("-")[-1]
        start = sizemap[size]
        prefix = True
    elif attribute_type.startswith("link-"):
        start = "["
        end = "]({})".format(html._decode_link(attribute_type))
    elif attribute_type.startswith("image"):
        start = "!["
        end = "]({})".format(html._decode_image(attribute_type).get("boxSharedLink"))
    elif attribute_type == "list":
        kind, level = html.get_list_info(box_attribute)
        if kind == 'ordered':
            formatter = '1. '
        elif kind == 'unordered':
            formatter = '* '
        elif kind == 'unchecked':
            formatter = '* [ ] '
        elif kind == 'checked':
            formatter = '* [x] '
        else:
            formatter = '* '
        start = "  " * (level - 1) + formatter
    return start, end, prefix
