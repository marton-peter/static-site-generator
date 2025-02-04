from enum import Enum

class TextType(Enum):
    NORMAL = "Normal text"
    BOLD = "Bold text"
    ITALIC = "Italic text"
    CODE = "Code text"
    LINK = "Link"
    IMAGE = "Image"

class TextNode ():
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, self.__class__):  # Ensure types match
            return False
        return self.text == other.text and \
            self.text_type == other.text_type and \
            self.url == other.url
        
    def __repr__(self):
        if self.url:
            return f"TextNode({self.text}, {self.text_type}, {self.url})"
        return f"TextNode({self.text}, {self.text_type})"
