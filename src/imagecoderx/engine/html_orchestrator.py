from bs4 import BeautifulSoup

def combine_html_sections(section_html_list, element_positions):
    """
    Merges multiple partial HTML sections into a final HTML document.
    """
    soup = BeautifulSoup("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Final Merged Output</title>
      <style>
      body { margin: 0; position: relative; }
      .element-section {
        position: absolute;
        box-sizing: border-box; /* Important for width/height */
      }
      </style>
    </head>
    <body></body>
    </html>
    """, "html.parser")

    body_tag = soup.find("body")
    style_tag = soup.find("style")

    for pos_info, raw_html in zip(element_positions, section_html_list):
        # Create a div for the section
        section_div = soup.new_tag("div", attrs={
            "class": "element-section",
            "style": (
                f"left:{pos_info['relative_x']*100}%; "
                f"top:{pos_info['relative_y']*100}%; "
                f"width:{pos_info['width']*100}%; "
                f"height:{pos_info['height']*100}%;"
            )
        })

        if pos_info.get("type") == "code":
            # Parse the HTML snippet
            sub_soup = BeautifulSoup(raw_html, "html.parser")

            # Extract and merge styles
            snippet_style = sub_soup.find("style")
            if snippet_style:
                style_tag.append(snippet_style.string)

            # Extract and append body content
            snippet_body = sub_soup.find("body")
            if snippet_body:
                for child in snippet_body.contents:
                    section_div.append(child)
            else:
                section_div.string = raw_html  # If no body, treat as plain text

        elif pos_info.get("type") == "logo":
            # Place the image
            img_tag = soup.new_tag("img", src=pos_info["filename"])
            section_div.append(img_tag)

        else:
            # Background or shape
            if pos_info.get("filename"):
                img_tag = soup.new_tag("img", src=pos_info["filename"])
                section_div.append(img_tag)

        body_tag.append(section_div)

    return str(soup)
