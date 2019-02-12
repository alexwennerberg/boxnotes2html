from boxnotes2html import html


def test_html_tag_conversion():
    bold = ["bold", "true"]
    assert html.convert_simple_element_to_html_tag(bold) == html.HTMLTag("b", {})


def test_url_conversion():
    url = "link-MTU0MTI5MDcxMzcxMC1odHRwczovL2Vtb2ppcGVkaWEub3JnL3NtaWxpbmctZmFjZS13aXRoLWhlYXJ0LXNoYXBlZC1leWVzLw=="
    assert (
        html._decode_link(url)
        == "https://emojipedia.org/smiling-face-with-heart-shaped-eyes/"
    )


def test_image_conversion():
    image = "image-305f112d24f84324805f3eaa9e64ecbe-JTdCJTIyYm94U2hhcmVkTGluayUyMiUzQSUyMmh0dHBzJTNBJTJGJTJGYXBwLmJveC5jb20lMkZzJTJGMnU0MXE5aTdrb25mcjBlYWZzOW45NHoyY2hqbXB1ZGglMjIlMkMlMjJib3hGaWxlSWQlMjIlM0ElMjIzNDM3ODk3NTE2MzUlMjIlMkMlMjJmaWxlTmFtZSUyMiUzQSUyMm9wZW5zb3VyY2VwYXJyb3QuZ2lmJTIyJTdE"
    assert (
        html._decode_image(image)["boxSharedLink"]
        == "https://app.box.com/s/2u41q9i7konfr0eafs9n94z2chjmpudh"
    )
