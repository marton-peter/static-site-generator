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
    for node in old_nodes: # Makes sure normal text nodes are not processed.
        if node.text_type is not TextType.NORMAL or delimiter not in node.text: # Appends the entire node if no delimiters were found.
            split_nodes.append(node)
            continue
        else:
            delimiter_stack = []
            delimiter_locations = {}
            last_delimiter_index = 0
            i = 0
            
            while i < len(node.text): # Looks for delimiters in the old node.
                if node.text[i:i+len(delimiter)] == delimiter:
                    if delimiter_stack != [] and delimiter_stack[-1] != delimiter:
                        raise Exception("Invalid nesting of delimiters")
                    elif delimiter_stack != [] and delimiter_stack[-1] == delimiter: # Checks if the delimiter has a pair.
                        delimiter_stack.pop() # Removes the pair of delimiters from the stack.
                        delimiter_locations["closing"] = i # Marks the index.
                        # Creates new nodes based on the removed delimiter pair.
                        if last_delimiter_index == 0: # Checks for a stored value left by the last delimiter pair and uses it to index the first node.
                            split_nodes.append(TextNode(node.text[:delimiter_locations["opening"]], TextType.NORMAL))
                        else:
                            split_nodes.append(TextNode(node.text[last_delimiter_index + len(delimiter):delimiter_locations["opening"]], TextType.NORMAL))
                        split_nodes.append(TextNode(node.text[delimiter_locations["opening"] + len(delimiter):delimiter_locations["closing"]], text_type))
                        last_delimiter_index = i # Saves the index for reference to the next pair of delimiters.
                    else: # Declares opening delimiter, adds it to the stack and marks the index.
                        delimiter_stack.append(delimiter)
                        delimiter_locations["opening"] = i
                    i += len(delimiter) # Makes sure the delimiter is not checked again.
                else:
                    i += 1

            if delimiter_stack != []: # Checks for unpaired delimiters.
                raise Exception("Invalid Markdown syntax")
            else:
                split_nodes.append(TextNode(node.text[delimiter_locations["closing"] + len(delimiter):], TextType.NORMAL)) # Saves the closing node.

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



def main():
    Dummy = TextNode("This is a text node", "bold", "https://www.boot.dev")
    print(Dummy)

if __name__ == "__main__":
    main()