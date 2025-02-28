def markdown_to_blocks(markdown):
    print("Script is running!")
    print(f"Processing markdown: {markdown[:50]}...")
    
    split_blocks = []
    print(f"DEBUG: split_blocks currently: {split_blocks}")

    if markdown.strip() == "": # Handles empty or whitespace-only input.
        print(f"Returning from empty input, split_blocks: {split_blocks}")
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
            print(f"Debug: Code block detected and added: {code_block}")
            print(f"Debug: split_blocks after adding code block = {split_blocks}")
            remaining_text = stripped[closing_index + 6:].strip()
            print(f"Debug: Processing remaining text: {remaining_text}")

            if remaining_text.startswith("```") and remaining_text != "```":
                raise ValueError(
                    f"Unclosed code block detected in remaining markdown: {remaining_text}"
                )
            elif not remaining_text or remaining_text == "```":
                print("Debug: Remaining text is either empty or just a closing backtick.")
                return split_blocks
            else:
                split_blocks.extend(markdown_to_blocks(remaining_text)) # Recursively processes remaining content.

        else:
            raise ValueError(
            f"Unclosed code block detected in markdown starting with: {stripped[:30]}..."
        )

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
                print(f"DEBUG: Remaining text after heading: {remaining_text}")
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
        print(f"Debug: In quote block, split_blocks before recursion = {split_blocks}")
        split_blocks.extend(markdown_to_blocks("\n".join(stripped.split("\n")[line_count:]))) # Recursively processes the remaining text.

    elif stripped.startswith("* ") or stripped.startswith("- "): # Checks for unordered lists. 
        marker = stripped[0]
        lines = []
        newline_count = 0
        original_lines = stripped.split("\n")
        i = 0
        
        while i < len(original_lines):
            line = original_lines[i]
            print(f"DEBUG: Raw line: '{line}', Stripped line: '{line.strip()}'")
            if line == "": # Breaks after 2 consecutive empty lines.
                newline_count += 1
                if newline_count >= 2:
                    break
                if len(lines) > 0:  # Only allows blank lines if a list block exists.
                    lines.append("")
            elif line.startswith(f"{marker} "): # Adds valid list items.
                newline_count = 0
                print(f"List line found: {line}")
                lines.append(line)
            else:
                print(f"Non-list line found, finishing list block: {line}")
                break  # Stops processing for this block type to avoid mixing blocks.
            i += 1
        
        block = "\n".join(lines).strip()
        print(f"Debug: Collected list lines = {lines}")
        print(f"Debug: Final list block = {block}")
        print(f"Debug: Is block empty? {block == ''}")
        if block:
            print(f"Debug: Adding block to split_blocks: {block}")
            split_blocks.append(block) # Appends the list block.
            print(f"DEBUG: split_blocks currently: {split_blocks}")
        
        if i < len(original_lines): # Processes remaining lines.
            remaining_text = "\n".join(original_lines[i:])
            print(f"Debug: Remaining markdown text passed to recursion: {remaining_text}")
            print(f"Debug: Recursive input = {original_lines[i:]}")
            print(f"Debug: In ul block, split_blocks before recursion = {split_blocks}")
            recursive_blocks = markdown_to_blocks(remaining_text)
            split_blocks.extend(recursive_blocks)
            print(f"After recursion: split_blocks = {split_blocks}")

    elif stripped[:3] == "1. ": # Checks for ordered lists.
        lines = []
        newline_count = 0
        original_lines = stripped.split("\n")
        i = 0
        
        while i < len(original_lines):
            line = original_lines[i]
            print(f"Checking line: {line}")
            if line == "": # Breaks after 2 consecutive empty lines.
                newline_count += 1
                if newline_count >= 2:
                    print("Breaking after 2 consecutive empty lines.")
                    break
                lines.append("")
                print(f"Empty line added to lines: {lines}")
            elif is_ordered_list_item(line): # Adds valid list items.
                newline_count = 0
                lines.append(line)
                print(f"Ordered list item added: {line}")
            else:
                    print(f"Non-list line found, finishing list block: {line}")
                    break  # Stops processing for this block type to avoid mixing blocks.
            i += 1
        
        block = "\n".join(lines).strip()
        if block:  # Only appends non-empty blocks.
            split_blocks.append(block)
            print(f"DEBUG: split_blocks currently: {split_blocks}")
        
        remaining_lines = original_lines[i:]
        if remaining_lines:
            remaining_text = "\n".join(remaining_lines).strip()
            if remaining_text and remaining_text != stripped:  # Only recurse if we have new text.
                print(f"Debug: In ol block, split_blocks before recursion = {split_blocks}")
                split_blocks.extend(markdown_to_blocks(remaining_text))
                print(f"DEBUG: split_blocks currently: {split_blocks}")
            
    else:
        lines = stripped.split("\n")  # Splits markdown into individual lines.
        paragraph_lines = []  # To collect lines for the current paragraph.

        for i, line in enumerate(lines):
            line = line.strip()
            print(f"Processing line: '{line}'")

            # Break and process when encountering a block marker.
            if line.startswith("*") or line.startswith("-") or line.startswith(">") or line.startswith("#") or line.startswith("```") or is_ordered_list_item(line):
                if paragraph_lines: # Appends collected paragraph lines first as a single block.
                    split_blocks.append("\n".join(paragraph_lines))  # Joins lines with newlines to preserve formatting.
                    print(f"DEBUG: split_blocks currently: {split_blocks}")
                    paragraph_lines = []  # Resets for the next block.

                remaining_text = "\n".join(lines[i:]).strip()
                if remaining_text: # Recurse for remaining lines from the current marker onward.
                    remaining_blocks = markdown_to_blocks(remaining_text)
                    if remaining_blocks:  # Ensures `remaining_blocks` is not None.
                        print(f"Debug: In paragraph block, split_blocks before recursion = {split_blocks}")
                        split_blocks.extend(remaining_blocks)
                        print(f"DEBUG: split_blocks currently: {split_blocks}")
                    break  # Stops further looping as recursion will handle the rest.

            else: # Collects non-marker lines as part of the current paragraph.
                if line:
                    paragraph_lines.append(line)

        if paragraph_lines: # Appends trailing paragraph lines if no markers were found.
            split_blocks.append("\n".join(paragraph_lines))
            print(f"DEBUG: split_blocks currently: {split_blocks}")

    if not isinstance(split_blocks, list):
        raise AssertionError(f"split_blocks is {type(split_blocks)}, expected list")
    if len(split_blocks) == 0:
        raise AssertionError("split_blocks is empty unexpectedly!")
    print(f"Returning from function, split_blocks: {split_blocks}")
    return split_blocks

# Test case
markdown = """# Main Title

This is a *paragraph* with **bold** and *italic* text.

## Secondary Heading

Here's a list:
* First item with **bold**
* Second item with *italic*
* Third item with `code`

Here's a numbered list:
1. First numbered with *emphasis*
2. Second numbered with **strong**
3. Third numbered with `code`

> This is a blockquote
> With multiple lines
> And some **bold** text

```python
def hello_world():
    print("Hello!")
```
        
### Final Heading
Last paragraph with ***bold italic*** text."""

blocks = markdown_to_blocks(markdown)
print("Generated Blocks:", blocks)
print("Type of Generated Blocks:", type(blocks))