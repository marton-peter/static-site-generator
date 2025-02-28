import unittest
from main import text_node_to_html_node, \
    split_nodes_delimiter, \
    extract_markdown_images, \
    extract_markdown_links, \
    split_nodes_image, \
    split_nodes_link, \
    text_to_textnodes, \
    markdown_to_blocks, \
    block_to_block_type, \
    markdown_to_html_node
from textnode import TextNode, TextType
from leafnode import LeafNode
from htmlnode import HTMLNode

class TestMain(unittest.TestCase):
    def test_text_node_to_html_node_normal(self):
        node = TextNode("Hello World", TextType.NORMAL)
        expected = LeafNode(None, "Hello World")
        self.assertEqual(text_node_to_html_node(node), expected)

    def test_text_node_to_html_node_bold(self):
        node = TextNode("Hello World", TextType.BOLD)
        expected = LeafNode("strong", "Hello World")
        self.assertEqual(text_node_to_html_node(node), expected)

    def test_text_node_to_html_node_italic(self):
        node = TextNode("Hello World", TextType.ITALIC)
        expected = LeafNode("em", "Hello World")
        self.assertEqual(text_node_to_html_node(node), expected)

    def test_text_node_to_html_node_code(self):
        node = TextNode("This should be code", TextType.CODE)
        expected = LeafNode("code", "This should be code")
        self.assertEqual(text_node_to_html_node(node), expected)

    def test_text_node_to_html_node_link(self):
        node = TextNode("Click Me!", TextType.LINK, "https://www.google.com")
        expected = LeafNode("a", "Click Me!", props={"href": "https://www.google.com"})
        self.assertEqual(text_node_to_html_node(node), expected)

    def test_text_node_to_html_node_image(self):
        node = TextNode("alt text", TextType.IMAGE, "https://www.google.com")
        expected = LeafNode("img", "", props={"src": "https://www.google.com", "alt": "alt text"})
        self.assertEqual(text_node_to_html_node(node), expected)

    def test_text_node_to_html_node_invalid(self):
        node = TextNode("Hello World", None)
        with self.assertRaises(Exception) as context:
                text_node_to_html_node(node)
        self.assertEqual(str(context.exception), "Invalid TextType")

    def test_split_nodes_delimiter_no_delimiters(self):
        node = TextNode("Hello World", TextType.NORMAL)
        expected = [TextNode("Hello World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter([node]), expected)

    def test_split_nodes_delimiter_bold(self):
        nodes = [TextNode("Hello **bold** World", TextType.NORMAL),
                 TextNode("Hello **even bolder** World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("bold", TextType.BOLD),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even bolder", TextType.BOLD),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes), expected)

    def test_split_nodes_delimiter_italic(self):
        nodes = [TextNode("Hello *italic* World", TextType.NORMAL),
                 TextNode("Hello *even more italic* World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("italic", TextType.ITALIC),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even more italic", TextType.ITALIC),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes), expected)

    def test_split_nodes_delimiter_code(self):
        nodes = [TextNode("Hello `code` World", TextType.NORMAL),
                 TextNode("Hello `even more code` World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even more code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes), expected)

    def test_split_nodes_delimiter_start(self):
        nodes = [TextNode("`Hello code` World", TextType.NORMAL),
                TextNode("Hello `even more code` World", TextType.NORMAL)]
        expected = [TextNode("Hello code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even more code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes), expected)

    def test_split_nodes_delimiter_end(self):
        nodes = [TextNode("Hello `code World`", TextType.NORMAL),
                 TextNode("Hello `even more code` World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("code World", TextType.CODE),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even more code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes), expected)

    def test_split_nodes_delimiter_consequent(self):
        nodes = [TextNode("Hello `code` World", TextType.NORMAL),
                 TextNode("Hello `even` `more` `code` World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even", TextType.CODE),
                    TextNode(" ", TextType.NORMAL),
                    TextNode("more", TextType.CODE),
                    TextNode(" ", TextType.NORMAL),
                    TextNode("code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes), expected)
        
    def test_extract_markdown_images_after_link(self):
        text = "[link](https://boot.dev)![image](https://image.jpg)"
        expected = [("image", "https://image.jpg")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_images_before_link(self):
        text = "![image](https://image.jpg)[link](https://boot.dev)"
        expected = [("image", "https://image.jpg")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_links_after_image(self):
        text = "![image](https://image.jpg)[link](https://boot.dev)"
        expected = [("link", "https://boot.dev")]
        self.assertEqual(extract_markdown_links(text), expected)
   
    def test_extract_markdown_links_before_image(self):
        text = "[link](https://boot.dev)![image](https://image.jpg)"
        expected = [("link", "https://boot.dev")]
        self.assertEqual(extract_markdown_links(text), expected)

    def test_extract_markdown_images_witohut_url(self):
        text = "![image]()[link](https://boot.dev)"
        expected = [("image", "")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_images_special_characters(self):
        text = "![happy cat](https://example.com/my%20cat%20photo.jpg)"
        expected = [("happy cat", "https://example.com/my%20cat%20photo.jpg")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_images_multiple_hits(self):
        text = "![happy cat](https://example.com/my%20cat%20photo.jpg)![image](https://image.jpg)"
        expected = [("happy cat", "https://example.com/my%20cat%20photo.jpg"), ("image", "https://image.jpg")]
        self.assertEqual(extract_markdown_images(text), expected)

    def test_split_nodes_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.NORMAL,
        )
        expected = [
            TextNode("This is text with a link ", TextType.NORMAL),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.NORMAL),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertEqual(split_nodes_link([node]), expected)

    def test_split_nodes_link_start(self):
        node = TextNode(
            "[to youtube](https://www.youtube.com/@bootdotdev)This is text with a link at the start.",
            TextType.NORMAL,
        )
        expected = [
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            TextNode("This is text with a link at the start.", TextType.NORMAL),
        ]
        self.assertEqual(split_nodes_link([node]), expected)

    def test_split_nodes_link_no_link(self):
        node = TextNode(
            "This is text with no link at all.",
            TextType.NORMAL,
        )
        expected = [
            TextNode("This is text with no link at all.", TextType.NORMAL),
        ]
        self.assertEqual(split_nodes_link([node]), expected)

    def test_split_nodes_link_consecutive(self):
        node = TextNode(
            "This is text with two consecutive links.[to boot dev](https://www.boot.dev)[to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.NORMAL,
        )
        expected = [
            TextNode("This is text with two consecutive links.", TextType.NORMAL),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
        ]
        self.assertEqual(split_nodes_link([node]), expected)

    def test_split_nodes_image(self):
        node = TextNode(
            "This is text with an image ![happy cat](https://example.com/my%20cat%20photo.jpg) and ![image](https://image.jpg)",
            TextType.NORMAL,
        )
        expected = [
            TextNode("This is text with an image ", TextType.NORMAL),
            TextNode("happy cat", TextType.IMAGE, "https://example.com/my%20cat%20photo.jpg"),
            TextNode(" and ", TextType.NORMAL),
            TextNode("image", TextType.IMAGE, "https://image.jpg"),
        ]
        self.assertEqual(split_nodes_image([node]), expected)

    def test_text_to_textnodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        expected = [
            TextNode("This is ", TextType.NORMAL),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.NORMAL),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.NORMAL),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.NORMAL),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.NORMAL),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(text_to_textnodes(text), expected)

    def test_text_to_textnodes_nested_bold(self):
        text = "*text **bold** more text*"
        expected = [
            TextNode("text ", TextType.ITALIC),
            TextNode("bold", TextType.BOLD),
            TextNode(" more text", TextType.ITALIC),
        ]
        self.assertEqual(text_to_textnodes(text), expected)

    def test_text_to_textnodes_nested_italic(self):
        text = "**bold *italic* text**"
        expected = [
            TextNode("bold ", TextType.BOLD),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.BOLD),
        ]
        self.assertEqual(text_to_textnodes(text), expected)

    def test_text_to_textnodes_nested_bold_2(self):
        text = "This is *italic **and bold** italic*"
        expected = [
            TextNode("This is ", TextType.NORMAL),
            TextNode("italic ", TextType.ITALIC),
            TextNode("and bold", TextType.BOLD),
            TextNode(" italic", TextType.ITALIC),
        ]
        self.assertEqual(text_to_textnodes(text), expected)

    def test_markdown_to_blocks(self):
        text = "\n\n# Heading\n\nText\n\n* Item\n\n"
        expected = ["# Heading", "Text", "* Item"]
        self.assertEqual(markdown_to_blocks(text), expected)

    def test_markdown_to_blocks_code(self):
        text = "```python\ndef hello():\n    return \"world\"\n```\n\nNext paragraph\n\n```ruby\nputs \"another block\"\n```"
        expected = ["```python\ndef hello():\n    return \"world\"\n```", "Next paragraph", "```ruby\nputs \"another block\"\n```"]
        self.assertEqual(markdown_to_blocks(text), expected)

    def test_markdown_to_blocks_quotes(self):
        text = "> First line\n> Second line\n\n> Another quote"
        expected = ["> First line\n> Second line", "> Another quote"]
        self.assertEqual(markdown_to_blocks(text), expected)

    def test_markdown_to_blocks_unordered_list(self):
        text = "* First item\n\n* Second item\n\n\n* New list"
        expected = ["* First item\n\n* Second item", "* New list"]
        self.assertEqual(markdown_to_blocks(text), expected)

    def test_block_to_block_type_empty_lines(self):
        text = "1. First\n\n2. Second\n\n3. Third"
        expected = "ordered_list"
        self.assertEqual(block_to_block_type(text), expected)

    def test_block_to_block_type_wrong_order(self):
        text = "1. First\n2. Second\n4. Fourth"
        expected = "paragraph"
        self.assertEqual(block_to_block_type(text), expected)

    def test_block_to_block_type_mixed_markers(self):
        text = "* First\n- Second\n* Third"
        expected = "paragraph"
        self.assertEqual(block_to_block_type(text), expected)

    def test_block_to_block_type_mixed_quotes(self):
        text = ">mixed\n> spacing\n>is fine"
        expected = "quote"
        self.assertEqual(block_to_block_type(text), expected)

    def test_block_to_block_type_nospace_heading(self):
        text = "#NoSpace"
        expected = "paragraph"
        self.assertEqual(block_to_block_type(text), expected)

    def test_block_to_block_type_code(self):
        text = "```\nsome code\n```"
        expected = "code"
        self.assertEqual(block_to_block_type(text), expected)

    def test_block_to_block_type_7_heading(self):
        text = "####### Too many"
        expected = "paragraph"
        self.assertEqual(block_to_block_type(text), expected)

    def markdown_to_html_node(self):
        markdown = """# Heading
This is a paragraph."""
        expected = HTMLNode("div", None)

        h1 = HTMLNode("h1", None)
        h1.children = [LeafNode(None, "Heading")]

        p1 = HTMLNode("p", None)
        p1.children = [LeafNode(None, "This is a paragraph."),]
        expected.children = [h1, p1]
        assert markdown_to_html_node(markdown).to_html() == expected.to_html()

    def test_mixed_formatting(self):
        markdown = """# Main Title
This is a paragraph with **bold** and *italic* text.

> This is a blockquote
> with multiple lines

* List item 1
* List item 2"""
        expected = HTMLNode("div", None)

        h1 = HTMLNode("h1", None)
        h1.children = [LeafNode(None, "Main Title")]

        p1 = HTMLNode("p", None)
        p1.children = [
            LeafNode(None, "This is a paragraph with "),
            LeafNode("strong", "bold"),
            LeafNode(None, " and "),
            LeafNode("em", "italic"),
            LeafNode(None, " text.")
            ]
        
        blockquote = HTMLNode("blockquote", None)
        blockquote.children = [HTMLNode("p", None, children=[LeafNode(None, "This is a blockquote with multiple lines")])]

        ul = HTMLNode("ul", None)
        li1 = HTMLNode("li", None)
        li1.children = [LeafNode(None, "List item 1")]

        li2 = HTMLNode("li", None)
        li2.children = [LeafNode(None, "List item 2")]
        ul.children = [li1, li2]

        expected.children = [h1, p1, blockquote, ul]
        assert markdown_to_html_node(markdown).to_html() == expected.to_html()

    def test_ordered_list(self):
        markdown = """Here's a numbered list:
1. First numbered with *emphasis*
2. Second numbered with **strong**
3. Third numbered with `code`"""

        expected = HTMLNode("div", None)

        # Paragraph above the list
        p = HTMLNode("p", None)
        p.children = [LeafNode(None, "Here's a numbered list:")]

        # Ordered list
        ol = HTMLNode("ol", None)

        li1 = HTMLNode("li", None)
        li1.children = [
            LeafNode(None, "First numbered with "),
            LeafNode("em", "emphasis")
        ]

        li2 = HTMLNode("li", None)
        li2.children = [
            LeafNode(None, "Second numbered with "),
            LeafNode("strong", "strong")
        ]

        li3 = HTMLNode("li", None)
        li3.children = [
            LeafNode(None, "Third numbered with "),
            LeafNode("code", "code")
        ]

        # Add list items to the ordered list
        ol.children = [li1, li2, li3]

        # Add paragraph and ordered list to the expected structure
        expected.children = [p, ol]

        # Run the test
        assert markdown_to_html_node(markdown).to_html() == expected.to_html()


    def test_complex_markdown(self):
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
Last paragraph with **bold italic** text."""
    
        expected = HTMLNode("div", None)

        h1 = HTMLNode("h1", None)
        h1.children = [LeafNode(None, "Main Title")]

        p1 = HTMLNode("p", None)
        p1.children = [
        LeafNode(None, "This is a "),
        LeafNode("em", "paragraph"),
        LeafNode(None, " with "),
        LeafNode("strong", "bold"),
        LeafNode(None, " and "),
        LeafNode("em", "italic"),
        LeafNode(None, " text.")
        ]

        h2 = HTMLNode("h2", None)
        h2.children = [LeafNode(None, "Secondary Heading")]

        p2 = HTMLNode("p", None)
        p2.children = [LeafNode(None, "Here's a list:")]

        ul = HTMLNode("ul", None)
        li1 = HTMLNode("li", None)
        li1.children = [
            LeafNode(None, "First item with "),
            LeafNode("strong", "bold")
        ]

        li2 = HTMLNode("li", None)
        li2.children = [
            LeafNode(None, "Second item with "),
            LeafNode("em", "italic")
        ]

        li3 = HTMLNode("li", None)
        li3.children = [
            LeafNode(None, "Third item with "),
            LeafNode("code", "code")
        ]

        ul.children = [li1, li2, li3]

        p3 = HTMLNode("p", None)
        p3.children = [LeafNode(None, "Here's a numbered list:")]

        ol = HTMLNode("ol", None)
        li1 = HTMLNode("li", None)
        li1.children = [
            LeafNode(None, "First numbered with "),
            LeafNode("em", "emphasis")
        ]

        li2 = HTMLNode("li", None)
        li2.children = [
            LeafNode(None, "Second numbered with "),
            LeafNode("strong", "strong")
        ]

        li3 = HTMLNode("li", None)
        li3.children = [
            LeafNode(None, "Third numbered with "),
            LeafNode("code", "code")
        ]

        ol.children = [li1, li2, li3]

        blockquote = HTMLNode("blockquote", None)
        blockquote.children = [HTMLNode("p", None, children=[
        LeafNode(None, "This is a blockquote With multiple lines And some "),
        LeafNode("strong", "bold"),
        LeafNode(None, " text")
        ])]

        pre = HTMLNode("pre", None)
        code = HTMLNode("code", None)
        code.children = [
            LeafNode(None, "def hello_world():\n    print(\"Hello!\")")
        ]
        pre.children = [code]

        h3 = HTMLNode("h3", None)
        h3.children = [
            LeafNode(None, "Final Heading")
        ]

        p4 = HTMLNode("p", None)
        p4.children = [
            LeafNode(None, "Last paragraph with "),
            LeafNode("strong", "bold italic"),
            LeafNode(None, " text.")
        ]

        expected.children = [h1, p1, h2, p2, ul, p3, ol, blockquote, pre, h3, p4]
        assert markdown_to_html_node(markdown).to_html() == expected.to_html()

    def test_markdown_to_html_node(self):
        # Test case 1: Simple code block
        markdown1 = "```\nprint('hello')\n```"
        
        # Test case 2: Code block with language specification
        markdown2 = "```python\ndef example():\n    print('hello')\n```"
        
        # Test case 3: Code block with empty lines
        markdown3 = "```python\ndef example():\n\n    print('hello')\n\n```"
        
        # Test case 4: Code block with trailing spaces
        markdown4 = "```python\nprint('hello')    \nprint('world')  \n```"
        
        # Test case 5: Invalid code block (no content)
        markdown5 = "```\n```"
        
        # Test case 6: Code block with indentation
        markdown6 = """```python
    def example():
        if True:
            print('indented')
        return None
    ```"""

        # Run tests
        try:
            node1 = markdown_to_html_node(markdown1)
            node2 = markdown_to_html_node(markdown2)
            node3 = markdown_to_html_node(markdown3)
            node4 = markdown_to_html_node(markdown4)
            node6 = markdown_to_html_node(markdown6)
            
            # This should raise ValueError
            node5 = markdown_to_html_node(markdown5)
            print("Test 5 failed: Should have raised ValueError")
        except ValueError:
            print("Test 5 passed: Correctly raised ValueError for empty code block")
