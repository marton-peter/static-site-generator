from htmlnode import HTMLNode
from leafnode import LeafNode

class ParentNode (HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        # Tests for invalid input.
        if not self.children:
            raise ValueError("No children")
        for child in self.children:
            if not isinstance(child, (ParentNode, LeafNode)):
                raise TypeError(f"Invalid child node: {child}")
        if not self.tag:
            raise ValueError("Missing tag")
        
        # Generates HTML for all children with their own methods.
        children_list = [node.to_html() for node in self.children]
        
        return f"<{self.tag}{self.props.props_to_html()}>{"".join(children_list)}</{self.tag}>"
    
    def __repr__(self):
        children_repr = ", ".join(repr(child) for child in self.children)
        if self.props is None:
            return f"ParentNode(tag={self.tag!r}, children=[{children_repr}])"
        else:
            return f"ParentNode(tag={self.tag!r}, children=[{children_repr}], props={self.props})"
           