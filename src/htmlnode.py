class HTMLNode ():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children or []
        self.props = props

    def to_html(self):
        if self.tag is None:
            # If no tag, just render children concatenated together
            return "".join(child.to_html() for child in self.children) if self.children else ""
    
        # Start with opening tag
        html = f"<{self.tag}"
        
        # Add any props/attributes if they exist
        if self.props:
            for key, value in self.props.items():
                html += f' {key}="{value}"'
        
        # Close opening tag
        html += ">"
        
        # Add children's HTML if they exist
        if self.children:
            for child in self.children:
                html += child.to_html()
        
        # Add closing tag
        html += f"</{self.tag}>"
        
        return html
    
    def props_to_html(self):
        string = ""
        if not self.props:
            return ""
        for key, value in self.props.items():
            string += f' {key}="{value}"'
        return string
    
    def __repr__(self):
        return f"HTMLNode(tag={self.tag!r}, value={self.value!r}, children={self.children!r}, props={self.props})"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):  # Ensure types match
            return False
        return self.tag == other.tag and \
            self.value == other.value and \
            self.children == other.children and \
            self.props == other.props