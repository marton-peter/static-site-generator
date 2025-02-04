import re
from textnode import TextNode, TextType
from leafnode import LeafNode

def text_node_to_html_node(text_node):
    if text_node.text_type is TextType.NORMAL:
        return LeafNode("", text_node.text)
    if text_node.text_type is TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type is TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type is TextType.CODE:
        return LeafNode("code", text_node.text)
    if text_node.text_type is TextType.LINK:
        return LeafNode("a", text_node.text, props={"href": text_node.url})
    if text_node.text_type is TextType.IMAGE:
        return LeafNode("img", "", props={"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception("Invalid TextType")
    
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    split_nodes = []

    # Checks if the text_type is valid.
    if (delimiter == "**" and text_type != TextType.BOLD) or \
    (delimiter == "*" and text_type != TextType.ITALIC) or \
    (delimiter == "`" and text_type != TextType.CODE):
        raise ValueError(f"Incorrect text_type {text_type} for delimiter {delimiter}")

    # Creates new text nodes based on delimiter locations.
    for node in old_nodes:
        if not node.text:  # Skip empty nodes
            continue
        if node.text_type is not TextType.NORMAL or delimiter not in node.text:
            split_nodes.append(node)
            continue
        else:
            i = 0
            while i < len(node.text): # Looks for delimiters in the old node.
                opening_index = node.text.find(delimiter, i) # Marks the opening delimiter.
                if opening_index == -1:  # No more delimiters
                    remaining_text = node.text[i:]
                    if remaining_text:  # only append if there's actual text
                        split_nodes.append(TextNode(remaining_text, TextType.NORMAL))
                    break
                closing_index = node.text.find(delimiter, opening_index + len(delimiter)) # Marks the closing delimiter.
                if closing_index == -1: # No more delimiters, append remaining text
                    remaining_text = node.text[i:]
                    if remaining_text:  # only append if there's actual text
                        split_nodes.append(TextNode(node.text[i:], TextType.NORMAL))
                    break
                text_before = node.text[i:opening_index]
                if text_before:  # only append if there's actual text
                    split_nodes.append(TextNode(text_before, TextType.NORMAL))
                split_nodes.append(TextNode(node.text[opening_index + len(delimiter):closing_index], text_type))
                i = closing_index + len(delimiter) # Makes sure the delimiter is not checked again.

    return split_nodes

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes):
    split_nodes =[]
    for node in old_nodes:
        extracted_tuples = extract_markdown_images(node.text)
        if extracted_tuples == []: # Only processes nodes with images.
            split_nodes.append(node)
            continue
        else:
            remaining_text = node.text
            for tuple in extracted_tuples: # Slices the text before the image and appends it as a text node.
                sections = remaining_text.split(f"![{tuple[0]}]({tuple[1]})", maxsplit=1)
                remaining_text = sections[1] # Updates the remaining text for the next iteration.
                split_nodes.append(TextNode(sections[0], TextType.NORMAL))
                split_nodes.append(TextNode(tuple[0], TextType.IMAGE, tuple[1])) # Appends the image and url as a node.
            split_nodes.append(TextNode(remaining_text, TextType.NORMAL)) # Appends the remaining text after the loop completes.
    return split_nodes

def split_nodes_link(old_nodes):
    split_nodes =[]
    for node in old_nodes:
        extracted_tuples = extract_markdown_links(node.text)
        if extracted_tuples == []: # Only processes nodes with links.
            split_nodes.append(node)
            continue
        else:
            remaining_text = node.text
            for tuple in extracted_tuples: # Slices the text before the link and appends it as a text node.
                sections = remaining_text.split(f"[{tuple[0]}]({tuple[1]})", maxsplit=1)
                remaining_text = sections[1] # Updates the remaining text for the next iteration.
                split_nodes.append(TextNode(sections[0], TextType.NORMAL))
                split_nodes.append(TextNode(tuple[0], TextType.LINK, tuple[1])) # Appends the link as a node.
            split_nodes.append(TextNode(remaining_text, TextType.NORMAL)) # Appends the remaining text after the loop completes.
    return split_nodes

def text_to_textnodes(text):
    nodes = split_nodes_link([TextNode(text, TextType.NORMAL)])
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_delimiter(nodes, "**", text_type=TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", text_type=TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", text_type=TextType.CODE)
    return nodes

def main():
    Dummy = TextNode("This is a text node", "bold", "https://www.boot.dev")
    print(Dummy)

if __name__ == "__main__":
    main()