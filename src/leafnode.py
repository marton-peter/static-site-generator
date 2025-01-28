from htmlnode import HTMLNode

class LeafNode (HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if not self.value:
            raise ValueError
        if not self.tag:
            return self.value
        if not self.props:
            return f"<{self.tag}>{self.value}</{self.tag}>"
        else:
            return f"<{self.tag}{self.props.props_to_html()}>{self.value}</{self.tag}>"
        
    def __repr__(self):
        return f"LeafNode(tag={self.tag!r}, value={self.value!r}, props={self.props})"