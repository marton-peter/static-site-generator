from htmlnode import HTMLNode
from leafnode import LeafNode

class ParentNode (HTMLNode):
    def __init__(self, tag=None, children=None, props=None):
        self.tag = tag
        self.children = children or []
        self.props = props

    def to_html(self):
        if not self.tag:
            raise ValueError("Missing tag")
        if not self.children:
            raise ValueError("No children")
        
        children_html = [child.to_html() for child in self.children]
        
        # Create properties string if props exist
        props_html = ""
        if self.props:
            for key, value in self.props.items():
                props_html += f' {key}="{value}"'
        
        return f"<{self.tag}{props_html}>{''.join(children_html)}</{self.tag}>"
    
    def __repr__(self):
        if self.props is None:
            return f"ParentNode(tag={self.tag!r}, children={self.children!r})"
        else:
            return f"ParentNode(tag={self.tag!r}, children={self.children!r}, props={self.props!r})"
           