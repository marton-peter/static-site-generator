import re
import shutil
import os
import sys
from textnode import TextNode, TextType
from parentnode import ParentNode
from leafnode import LeafNode

def text_node_to_html_node(text_node):
    if text_node.text_type is TextType.NORMAL:
        return LeafNode(None, text_node.text)
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
        {TextType.BOLD: "**", TextType.ITALIC: "*", TextType.ITALIC: "_", TextType.CODE: "`"}.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    def find_matching_delimiter(text, delimiter, start_pos): # Finds the matching closing delimiter that isn't part of a larger delimiter.
        curr_pos = start_pos + len(delimiter)
        while curr_pos < len(text):
            if delimiter == "*" and text.startswith("**", curr_pos): # If delimiter is "*" and we find "**", skip it.
                curr_pos += 2
                continue
            if delimiter == "_" and text.startswith("__", curr_pos):  # Skips double underscores if using single.
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
                if not pairs_found or opening_delimiter is None:
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
    final_nodes = split_nodes_delimiter(nodes)
    return final_nodes

def markdown_to_blocks(markdown):
    split_blocks = []
    if markdown.strip() == "": # Handles empty or whitespace-only input.
        return split_blocks
    stripped = markdown.strip()

    def is_ordered_list_item(line):
        parts = line.split(".", 1) # Splits by first period.
        return len(parts) > 1 and parts[0].strip().isdigit() and parts[1].startswith(" ") # Checks if we have at least 2 parts and the first part is a number.

    if stripped.startswith("```"): # Checks for an opening code block.
        closing_index = stripped[3:].find("```") # Marks the end of the code block.

        if closing_index != -1:  # Ensures there's a closing ```.
            end_index = min(closing_index + 6, len(stripped))
            code_block = stripped[:end_index] # Extracts the entire block including both the opening and closing ```.
            split_blocks.append(code_block)
            remaining_text = stripped[closing_index + 6:].strip()

            if remaining_text.startswith("```") and remaining_text != "```":
                raise ValueError(f"Unclosed code block detected in remaining markdown: {remaining_text}")
            
            elif not remaining_text or remaining_text == "```":
                return split_blocks
            
            else:
                split_blocks.extend(markdown_to_blocks(remaining_text)) # Recursively processes remaining content.

        else:
            raise ValueError(f"Unclosed code block detected in markdown starting with: {stripped[:30]}...")

    elif stripped.startswith("#"):  # Checks for heading block.
        sharp_count = len(stripped.split(" ")[0])  # Counts the leading `#` characters.

        if 1 <= sharp_count <= 6 and stripped[sharp_count] == " ": # Extracts heading content.
            first_newline_index = stripped.find("\n")  # Finds where the heading ends.

            if first_newline_index == -1:  # If no newline, the entire string is considered heading.
                heading_content = stripped[sharp_count + 1:].strip()
                split_blocks.append(f"{'#' * sharp_count} {heading_content}")
                return split_blocks
            
            else:
                heading_content = stripped[sharp_count + 1:first_newline_index].strip()
                split_blocks.append(f"{'#' * sharp_count} {heading_content}") # Appends the isolated heading line.
                remaining_text = stripped[first_newline_index + 1:].strip()
                if remaining_text:
                    split_blocks.extend(markdown_to_blocks(remaining_text))  # Recursively processes remaining content.

    elif stripped.startswith(">"): # Checks for an opening quote block.
        line_count = 0 # Marks the end of the quote block.
        lines = []

        for line in stripped.split("\n"):
            if line.startswith(">"):
                line_count += 1
                lines.append(line.strip())

            else:
                break

        split_blocks.append("\n".join(lines)) # Appends the quote block.
        split_blocks.extend(markdown_to_blocks("\n".join(stripped.split("\n")[line_count:]))) # Recursively processes the remaining text.

    elif stripped.startswith("* ") or stripped.startswith("- "): # Checks for unordered lists. 
        marker = stripped[0]
        lines = []
        newline_count = 0
        original_lines = stripped.split("\n")
        i = 0
        
        while i < len(original_lines):
            line = original_lines[i]
            if line == "": # Breaks after 2 consecutive empty lines.
                newline_count += 1
                if newline_count >= 2:
                    break
                if len(lines) > 0:  # Only allows blank lines if a list block exists.
                    lines.append("")
            elif line.startswith(f"{marker} "): # Adds valid list items.
                newline_count = 0
                lines.append(line)
            else:
                break  # Stops processing for this block type to avoid mixing blocks.
            i += 1
        
        block = "\n".join(lines).strip()
        if block:
            split_blocks.append(block) # Appends the list block.
        
        if i < len(original_lines): # Processes remaining lines.
            remaining_text = "\n".join(original_lines[i:])
            recursive_blocks = markdown_to_blocks(remaining_text)
            split_blocks.extend(recursive_blocks)

    elif stripped[:3] == "1. ": # Checks for ordered lists.
        lines = []
        newline_count = 0
        original_lines = stripped.split("\n")
        i = 0
        
        while i < len(original_lines):
            line = original_lines[i]
            if line == "": # Breaks after 2 consecutive empty lines.
                newline_count += 1
                if newline_count >= 2:
                    break
                lines.append("")

            elif is_ordered_list_item(line): # Adds valid list items.
                newline_count = 0
                lines.append(line)

            else:
                    break  # Stops processing for this block type to avoid mixing blocks.
            i += 1
        
        block = "\n".join(lines).strip()
        if block:  # Only appends non-empty blocks.
            split_blocks.append(block)
        
        remaining_lines = original_lines[i:]
        if remaining_lines:
            remaining_text = "\n".join(remaining_lines).strip()
            if remaining_text and remaining_text != stripped:  # Only recurse if we have new text.
                split_blocks.extend(markdown_to_blocks(remaining_text))
            
    else:
        lines = stripped.split("\n")  # Splits markdown into individual lines.
        paragraph_lines = []

        for i, line in enumerate(lines):
            line = line.strip()

            if line.startswith("* ") or \
                line.startswith("- ") or \
                line.startswith(">") or \
                line.startswith("#") or \
                line.startswith("```") or \
                is_ordered_list_item(line): # Breaks and processes when encountering a block marker.
                if paragraph_lines: # Appends collected paragraph lines first as a single block.
                    split_blocks.append("\n".join(paragraph_lines))  # Joins lines with newlines to preserve formatting.
                    paragraph_lines = []  # Resets for the next block.

                remaining_text = "\n".join(lines[i:]).strip()
                if remaining_text == markdown:
                    print(f"Unexpected stalling input: '{remaining_text[:30]}...'")
                    raise ValueError("Unable to process remaining markdown.")
                if remaining_text: # Recurse for remaining lines from the current marker onward.
                    remaining_blocks = markdown_to_blocks(remaining_text)
                    if remaining_blocks:  # Ensures `remaining_blocks` is not None.
                        split_blocks.extend(remaining_blocks)
                    break  # Stops further looping as recursion will handle the rest.

            else: # Collects non-marker lines as part of the current paragraph.
                if line:
                    paragraph_lines.append(line)

        if paragraph_lines: # Appends trailing paragraph lines if no markers were found.
            split_blocks.append("\n".join(paragraph_lines))

    if not isinstance(split_blocks, list):
        raise AssertionError(f"split_blocks is {type(split_blocks)}, expected list")
    if len(split_blocks) == 0:
        raise AssertionError("split_blocks is empty unexpectedly!")
    return split_blocks

def block_to_block_type(markdown_block):
    if markdown_block[:3] == "```" and markdown_block[-3:] == "```": # Code blocks: Checks for triple backticks at start and end.
        return "code"
    elif markdown_block[0] == '#': # Headings: Checks for 1-6 #'s followed by space.
        count = 0
        for char in markdown_block[:6]:
            if char == '#':
                count += 1
            else:
                break
        if 0 < count <= 6 and markdown_block[count] == ' ':
            return "heading"
        else:
            return "paragraph"
    elif markdown_block[0] == ">": # Quotes: All non-empty lines must start with ">".
        passed = True
        for line in markdown_block.split("\n"):
            if line == "":
                continue
            if line[0] != ">":
                passed = False
        if passed:
            return "quote"
        else:
            return "paragraph"
    elif markdown_block[:2] == "* " or markdown_block[:2] == "- ": # Unordered lists: All non-empty lines must start with either "* " or "- ".
        marker = markdown_block[0]
        passed = True
        for line in markdown_block.split("\n"):
            if line == "":
                continue
            if line[:2] != f"{marker} ":
                passed = False
        if passed:
            return "unordered_list"
        else:
            return "paragraph"
    elif markdown_block[:3] == "1. ": # Ordered lists: Must start with "1. " and each subsequent non-empty line must increment.
        passed = True
        count = 1
        for line in markdown_block.split("\n"):
            if line == "":
                continue
            if line[:len(str(count)) + 2] != f"{count}. ":
                passed = False
            count += 1
        if passed:
            return "ordered_list"
        else:
            return "paragraph"
    else: # Paragraphs: Anything that doesn’t match the above.
        return "paragraph"

def markdown_to_html_node(markdown):

    def process_list_items(block, ordered=False):
        lines = block.split('\n')
        items = []
        current_item = []
        
        for line in lines: # Checks for both unordered and ordered list markers.
            is_new_item = False
            if not ordered and (line.startswith('* ') or line.startswith('- ')):
                is_new_item = True
                line = line[2:]  # Removes '* ' or '- '.
            elif ordered and re.match(r'^\d+\.\s', line):
                is_new_item = True
                line = re.sub(r'^\d+\.\s+', '', line)  # Removes the "1. " part.
                
            if is_new_item:
                if current_item:
                    items.append('\n'.join(current_item))
                current_item = [line]
            elif line.strip() == '': # Empty line
                if current_item:
                    current_item.append(line)
            elif line.startswith('  '): # Indented continuation line
                if current_item:
                    current_item.append(line.strip())
            else: # Any other line
                if current_item:
                    current_item.append(line.strip())
        
        if current_item: # Appends the last item.
            items.append('\n'.join(current_item))
        return items

    blocks = markdown_to_blocks(markdown)
    div = ParentNode("div", None) # Creates the main container node.
    nodes = []

    for block in blocks:
        if block_to_block_type(block) == "code": # Wraps blocks in nested nodes and removes the first and last lines.
            outer_node = ParentNode('pre', None)
            lines = block.split("\n")
            if len(lines) < 3:  # Needs at least opening, content, and closing lines.
                raise ValueError("Invalid code block")
            if lines and lines[0].strip().startswith("```"): # Removes the opening line with backticks (regardless of language identifier).
                lines = lines[1:]
            if lines and lines[-1].strip() == "```": # Removes the closing line with backticks.
                lines = lines[:-1]
            inner_node = ParentNode("code", None)
            inner_node.children = [LeafNode(None, "\n".join(lines))]
            outer_node.children = [inner_node]
            nodes.append(outer_node)

        elif block_to_block_type(block) == "heading": # Wraps heading blocks in the right node type and processes the text further.
            count = len(block) - len(block.lstrip('#'))
            lines = block.split("\n", maxsplit = 1)
            outer_node = ParentNode(f'h{count}', None)
            text_node = text_to_textnodes(lines[0].lstrip('#').strip())
            inner_node = [text_node_to_html_node(node) for node in text_node]
            outer_node.children = inner_node
            nodes.append(outer_node)
            if len(lines) > 1: # Appends the remaining text as a paragraph.
                paragraph_outer_node = ParentNode(f'p', None)
                text_nodes = text_to_textnodes(lines[1])
                paragraph_inner_nodes = [text_node_to_html_node(node) for node in text_nodes]
                paragraph_outer_node.children = paragraph_inner_nodes
                nodes.append(paragraph_outer_node)

        elif block_to_block_type(block) == "quote": # Wraps quote blocks in a parent node, strips '>' from the beginning of lines and processes the text further.
            outer_node = ParentNode('blockquote', None)
            lines = block.split("\n")
            stripped_lines = [line.lstrip('>').strip() for line in lines]
            text = " ".join(stripped_lines)
            text = re.sub(r'\s+', ' ', text)
            text_node = LeafNode(None, text)
            outer_node.children = [text_node]
            nodes.append(outer_node)

        elif block_to_block_type(block) == "unordered_list": # Wraps unordered lists in a parent node, strips '* ' or '- ' from the beginning of lines and wraps them in 'li' nodes before processing them furter.
            outer_node = ParentNode('ul', None)
            items = process_list_items(block, ordered=False)
            li_nodes = []
            for item in items:
                li_node = ParentNode('li', None)
                text_nodes = text_to_textnodes(item)
                inner_nodes = [text_node_to_html_node(node) for node in text_nodes]
                li_node.children = inner_nodes
                li_nodes.append(li_node)
            outer_node.children = li_nodes
            nodes.append(outer_node)

        elif block_to_block_type(block) == "ordered_list": # Wraps ordered lists in a parent node, strips numbers and periods from the beginning of lines and wraps them in 'li' nodes before processing them furter.
            outer_node = ParentNode('ol', None)
            items = process_list_items(block, ordered=True)
            li_nodes = []
            for item in items:
                li_node = ParentNode('li', None)
                text_nodes = text_to_textnodes(item)
                inner_nodes = [text_node_to_html_node(node) for node in text_nodes]
                li_node.children = inner_nodes
                li_nodes.append(li_node)
            outer_node.children = li_nodes
            nodes.append(outer_node)

        elif block_to_block_type(block) == "paragraph": # Wraps paragraph blocks in a parent node type and processes the text further.
            outer_node = ParentNode(f'p', None)
            text_nodes = text_to_textnodes(block)
            inner_nodes = [text_node_to_html_node(node) for node in text_nodes]
            outer_node.children = inner_nodes
            nodes.append(outer_node)

        else:
            raise ValueError("Invalid markdown format")

    div.children = nodes
    return div

def copy_dir_contents(source_path, dest_path):
    source_path = os.path.normpath(source_path)
    dest_path = os.path.normpath(dest_path)
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
        os.mkdir(dest_path)
        print("Destination folder cleaned and recreated")
    else:
        os.mkdir(dest_path)
        print("Destination folder created")

    if not os.path.exists(source_path):
        raise Exception(f"Invalid source path: {source_path}")
    
    contents = os.listdir(path=source_path)
    if not contents:
        print(f"No files or subdirectories to copy: {source_path}")
    else:
        for item in contents:
            source_item = os.path.join(source_path, item)
            dest_item = os.path.join(dest_path, item)
            if os.path.isfile(source_item):
                try:
                    shutil.copy(source_item, dest_item)
                    print(f"File copied: {source_item}")
                except Exception as e:
                    print(f"Error copying file {source_item}: {e}")
            else:
                try:
                    os.mkdir(dest_item)
                    print(f"Directory created: {dest_item}")
                    copy_dir_contents(source_item, dest_item)
                except Exception as e:
                    print(f"Error creating directory {dest_item}: {e}")

def extract_title(markdown):
    stripped = markdown.strip()
    if stripped == "": # Handles empty or whitespace-only input.
        raise ValueError("Empty input string")
    lines = stripped.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("No h1 header found")

def generate_page(source_path, template_path, dest_path, basepath):
    print(f"Generating page from {source_path} to {dest_path} using {template_path}")
    with open(source_path) as f:
        markdown = f.read()
    with open(template_path) as f:
        template = f.read()
    html_str = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html_str)
    template = template.replace('href="/', f'href="{basepath}')
    template = template.replace('src="/', f'src="{basepath}')
    dest_dir = os.path.dirname(dest_path)
    os.makedirs(dest_dir, exist_ok=True)
    print("Destination directory created: ", dest_dir)
    with open(dest_path, 'w') as f:
        f.write(template)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    dir_path_content = os.path.normpath(dir_path_content)
    template_path = os.path.normpath(template_path)
    dest_dir_path = os.path.normpath(dest_dir_path)
    
    if not os.path.exists(dir_path_content):
        raise Exception(f"Invalid content path: {dir_path_content}")
    
    contents = os.listdir(path=dir_path_content)
    if not contents:
        print(f"No files or subdirectories in content directory: {dir_path_content}")
    else:
        for item in contents:
            content_item = os.path.join(dir_path_content, item)
            dest_item = os.path.join(dest_dir_path, item)
            if os.path.isfile(content_item) and content_item[-3:] == ".md":
                try:
                    generate_page(content_item, template_path, os.path.join(dest_dir_path, "index.html"), basepath)
                except Exception as e:
                    print(f"Could not generate page from {content_item}: {e}")
            elif os.path.isdir(content_item):
                try:
                    os.makedirs(dest_item, exist_ok=True)
                    print(f"Directory ensured: {dest_item}")
                    generate_pages_recursive(content_item, template_path, dest_item, basepath)
                except Exception as e:
                    print(f"Error creating directory {dest_item}: {e}")
    

def main():
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"
    copy_dir_contents("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)

if __name__ == "__main__":
    main()
