class HTMLNode ():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
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