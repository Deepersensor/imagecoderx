from bs4 import BeautifulSoup

def combine_html_sections(section_html_list, element_positions):
    """
    Merges multiple partial HTML sections into a final HTML document.
    Each section_html_list item corresponds to a piece of HTML from a region.
    element_positions is a list of dicts containing info such as:
      {
        "type": "logo" or "code" or "background",
        "relative_x": 0.10,
        "relative_y": 0.20,
        "width": 120,
        "height": 80,
        "filename": "region_2_no_bg.png",
        "html_snippet": "<div>...</div>"
      }
    Returns a final combined HTML string.
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
      }
      </style>
    </head>
    <body></body>
    </html>
    """, "html.parser")

    body_tag = soup.find("body")

    for pos_info, raw_html in zip(element_positions, section_html_list):
        sub_soup = BeautifulSoup(raw_html, "html.parser")
        if pos_info.get("type") == "code":
            # Merge body & style if present
            snippet_body = sub_soup.find("body")
            snippet_style = sub_soup.find("style")
            snippet_div = soup.new_tag("div", attrs={
                "class": "element-section",
                "style": f"left:{pos_info['relative_x']*100}%; top:{pos_info['relative_y']*100}%;"
            })
            if snippet_body:
                for child in snippet_body.contents:
                    snippet_div.append(child)
            else:
                snippet_div.string = raw_html
            if snippet_style:
                main_style = soup.find("style")
                main_style.append(snippet_style.string)
            body_tag.append(snippet_div)
        elif pos_info.get("type") == "logo":
            # Place the image
            img_tag = soup.new_tag("img", src=pos_info["filename"], attrs={
                "class": "element-section",
                "style": f"left:{pos_info['relative_x']*100}%; top:{pos_info['relative_y']*100}%;"
            })
            body_tag.append(img_tag)
        else:
            # Background or shape
            div_tag = soup.new_tag("div", attrs={
                "class": "element-section",
                "style": f"left:{pos_info['relative_x']*100}%; top:{pos_info['relative_y']*100}%;"
            })
            if pos_info.get("filename"):
                # Could also reference color alone
                img_tag = soup.new_tag("img", src=pos_info["filename"])
                div_tag.append(img_tag)
            body_tag.append(div_tag)

    return str(soup)
