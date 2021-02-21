"""
Some helper functions for converting box attributes to HTML
"""
import base64
import json
import urllib.parse
from collections import namedtuple

HTMLTag = namedtuple("HTMLTag", ["tag", "attributes"])


def get_table_info(box_attribute):
    attribute_type = box_attribute[0]
    if attribute_type.startswith("struct-table"):
        table_id = attribute_type.partition("_")[0].replace("struct-table", "")
        if "_row" in attribute_type:  # col and row backwards
            row_id = attribute_type.partition("_row")[2]
            return table_id, row_id, None
        elif "_col" in attribute_type:
            col_id = attribute_type.partition("_col")[2]
            return table_id, None, col_id
    return None, None, None


def get_list_attribute(box_attribute):  # UNUSED
    # ordered vs unordered
    attribute_type = box_attribute[1][:-1]
    if attribute_type.startswith("number"):
        return HTMLTag("ol", {})
    else:
        return HTMLTag("ul", {})  # set defautl value


def get_list_info(box_attribute):
    if "list" in box_attribute[0]:
        if box_attribute[1].startswith("number"):
            kind = "ordered"
        elif box_attribute[1].startswith("uncheck"):
            kind = "unchecked"
        elif box_attribute[1].startswith("check"):
            kind = "checked"
        else:
            kind = "unordered"
        # TODO: regex. cant do more than 9 list levels
        return kind, int(box_attribute[1][-1])


def convert_simple_element_to_html_tag(box_attribute):
    tag = None
    html_attrib = {}
    attribute_type = box_attribute[0]
    attribute_value = box_attribute[1]
    assert attribute_value  # WIP
    if attribute_type == "bold":
        tag = "b"
    elif attribute_type == "underline":
        tag = "u"
    elif attribute_type == "italic":
        tag = "i"
    elif attribute_type == "strikethrough":
        tag = "s"
    elif "font-color" in attribute_type:
        tag = "font"
        html_attrib = {"color": attribute_type.split("-")[-1]}
    elif "font-size" in attribute_type:
        tag = "font"
        size = attribute_type.split("-")[-1]
        sizemap = {
            "medium": "3",
            "large": "+2",
            "verylarge": "+3",
            "small": "-1",  # TODO: consider
        }
        html_attrib["size"] = sizemap[size]
    elif attribute_type == "align":
        tag = "div"
        html_attrib["style"] = "text-align: {}".format(attribute_value)
    elif attribute_type.startswith("link-"):
        urlstring = _decode_link(attribute_type)
        tag = "a"
        html_attrib["href"] = urlstring
    elif attribute_type.startswith("image"):
        tag = "img"
        html_attrib["src"] = _decode_image(attribute_type).get("boxSharedLink")
    # elif attribute_type.startswith("struct-table"):
    #    tag = "td"
    elif attribute_type == "list":
        if "checked" in attribute_value:  # "checked" or "unckecked"
            tag = "input"
            html_attrib["type"] = "checkbox"
            if attribute_value.startswith("checked"):
                html_attrib["checked"] = "checked"
        else:
            tag = "li"
    return HTMLTag(tag, html_attrib)  # NamedTuple


def _decode_link(urlstring):  # move to separate module
    return base64.b64decode(urlstring.split("-")[-1]).decode("utf-8").partition("-")[2]


def _decode_image(imagestring):
    # distinguish image flags..."
    # this one is fun
    return json.loads(
        urllib.parse.unquote(
            base64.b64decode(imagestring.split("-")[-1]).decode("utf-8")
        )
    )
