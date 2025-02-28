from htmlnode import HTMLNode

class LeafNode (HTMLNode):
    def __init__(self, tag, value, props=None):
        if value is None:
            raise ValueError("LeafNode value cannot be None")
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.tag is None:
            return self.value
        if self.props is None:
            return f"<{self.tag}>{self.value}</{self.tag}>"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
        
    def __repr__(self):
        if self.props is None:
            return f"LeafNode(tag={self.tag!r}, value={self.value!r})"
        else:
            return f"LeafNode(tag={self.tag!r}, value={self.value!r}, props={self.props})"