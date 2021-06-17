def create_xml_tag(name: str, content: str) -> str:
    opening_tag = "<"  + name + ">"
    closing_tag = "</" + name + ">"

    return opening_tag + content + closing_tag
