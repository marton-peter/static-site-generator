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
    
def split_nodes_delimiter(old_nodes):
    split_nodes = []
    delimiters = sorted(
        {TextType.BOLD: "**", TextType.ITALIC: "*", TextType.CODE: "`"}.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    def find_matching_delimiter(text, delimiter, start_pos): # Finds the matching closing delimiter that isn't part of a larger delimiter
        curr_pos = start_pos + len(delimiter)
        while curr_pos < len(text):
            if delimiter == "*" and text.startswith("**", curr_pos): # If delimiter is "*" and we find "**", skip it
                curr_pos += 2
                continue
            if text.startswith(delimiter, curr_pos): # If we find our delimiter
             return curr_pos
            curr_pos += 1
        return -1

    for node in old_nodes:
        if node.text_type in [TextType.IMAGE, TextType.LINK]: # Skips link or image nodes.
            split_nodes.append(node)
        else:
            i = 0
            pairs_found = False
            while i < len(node.text): # Looks for delimiters in the text.
                starting_index = None
                opening_delimiter = None
                closing_index = None
                for delim_type, delim_str in delimiters: # Looks for the first delimiter pair in the text.
                    opening_index = node.text.find(delim_str, i) # Marks the index of the first delimiter found.
                    if opening_index == -1:
                        continue
                    ending_index = find_matching_delimiter(node.text, delim_str, opening_index) # Marks corresponding closing delimiter.
                    if ending_index == -1:
                        continue
                    if starting_index is None or opening_index < starting_index: # Checks if the pair of delimiters is the first in the text. 
                        opening_delimiter = (delim_type, delim_str)
                        closing_index = ending_index
                        starting_index = opening_index
                        pairs_found = True
                if not pairs_found:
                    break
                elif opening_delimiter is None:
                    break
                else:
                    text_before = node.text[i:starting_index]
                    if text_before:  # Only appends the node if there's actual text.
                        split_nodes.append(TextNode(text_before, node.text_type)) # Appends the text before the opening delimiter.
                    split_nodes.extend(split_nodes_delimiter([TextNode(node.text[starting_index + len(opening_delimiter[1]):closing_index], opening_delimiter[0])])) # Appends the text between delimiters after processing nested nodes.
                i = closing_index + len(opening_delimiter[1]) # Advances the loop.
            if not pairs_found:
                    split_nodes.append(node)
            elif i < len(node.text): # Appends any trailing text after the loop completes.
                trailing_text = node.text[i:]
                if not split_nodes or split_nodes[-1].text != trailing_text:  # Avoids appending duplicate trailing text.
                    split_nodes.append(TextNode(trailing_text, node.text_type))
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
        if extracted_tuples == [] or node.text_type != TextType.NORMAL: # Only processes NORMAL nodes with images.
            split_nodes.append(node)
            continue
        else:
            remaining_text = node.text
            for t in extracted_tuples: # Slices the text before the image and appends it as a text node.
                sections = remaining_text.split(f"![{t[0]}]({t[1]})", maxsplit=1)
                remaining_text = sections[1] # Updates the remaining text for the next iteration.
                if sections[0] != "": # Only appends the node if there's actual text.
                    split_nodes.append(TextNode(sections[0], TextType.NORMAL)) # Appends the text before the image and url as a node.
                split_nodes.append(TextNode(t[0], TextType.IMAGE, t[1])) # Appends the image and url as a node.
            if remaining_text: # Only appends the node if there's actual text.
                split_nodes.append(TextNode(remaining_text, TextType.NORMAL)) # Appends the remaining text after the loop completes.
    return split_nodes

def split_nodes_link(old_nodes):
    split_nodes =[]
    for node in old_nodes:
        extracted_tuples = extract_markdown_links(node.text)
        if extracted_tuples == [] or node.text_type != TextType.NORMAL: # Only processes NORMAL nodes with links.
            split_nodes.append(node)
            continue
        else:
            remaining_text = node.text
            for t in extracted_tuples: # Slices the text before the link and appends it as a text node.
                sections = remaining_text.split(f"[{t[0]}]({t[1]})", maxsplit=1)
                remaining_text = sections[1] # Updates the remaining text for the next iteration.
                if sections[0] != "": # Only appends the node if there's actual text.
                    split_nodes.append(TextNode(sections[0], TextType.NORMAL)) # Appends the text before the link as a node.
                split_nodes.append(TextNode(t[0], TextType.LINK, t[1])) # Appends the link as a node.
            if remaining_text: # Only appends the node if there's actual text.
                split_nodes.append(TextNode(remaining_text, TextType.NORMAL)) # Appends the remaining text after the loop completes.
    return split_nodes

def text_to_textnodes(text):
    nodes = split_nodes_link([TextNode(text, TextType.NORMAL)])
    nodes = split_nodes_image(nodes)
    return split_nodes_delimiter(nodes)

def main():
    Dummy = TextNode("This is a text node", "bold", "https://www.boot.dev")
    print(Dummy)

if __name__ == "__main__":
    main()
