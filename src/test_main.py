import unittest
from main import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes
from textnode import TextNode, TextType
from leafnode import LeafNode

class TestMain(unittest.TestCase):
    def test_text_node_to_html_node_normal(self):
        node = TextNode("Hello World", TextType.NORMAL)
        expected = LeafNode("", "Hello World")
        self.assertEqual(text_node_to_html_node(node), expected)

    def test_text_node_to_html_node_bold(self):
        node = TextNode("Hello World", TextType.BOLD)
        expected = LeafNode("b", "Hello World")
        self.assertEqual(text_node_to_html_node(node), expected)

    def test_text_node_to_html_node_italic(self):
        node = TextNode("Hello World", TextType.ITALIC)
        expected = LeafNode("i", "Hello World")
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
        self.assertEqual(split_nodes_delimiter([node], "**", TextType.BOLD), expected)

    def test_split_nodes_delimiter_bold(self):
        nodes = [TextNode("Hello **bold** World", TextType.NORMAL),
                 TextNode("Hello **even bolder** World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("bold", TextType.BOLD),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even bolder", TextType.BOLD),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes, "**", TextType.BOLD), expected)

    def test_split_nodes_delimiter_italic(self):
        nodes = [TextNode("Hello *italic* World", TextType.NORMAL),
                 TextNode("Hello *even more italic* World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("italic", TextType.ITALIC),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even more italic", TextType.ITALIC),
                    TextNode(" World", TextType.NORMAL)]
        
        self.assertEqual(split_nodes_delimiter(nodes, "*", TextType.ITALIC), expected)

    def test_split_nodes_delimiter_code(self):
        nodes = [TextNode("Hello `code` World", TextType.NORMAL),
                 TextNode("Hello `even more code` World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even more code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes, "`", TextType.CODE), expected)

    def test_split_nodes_delimiter_start(self):
        nodes = [TextNode("", TextType.NORMAL),
                TextNode("`Hello code` World", TextType.NORMAL),
                TextNode("Hello `even more code` World", TextType.NORMAL)]
        expected = [TextNode("Hello code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even more code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes, "`", TextType.CODE), expected)

    def test_split_nodes_delimiter_end(self):
        nodes = [TextNode("Hello `code World`", TextType.NORMAL),
                 TextNode("Hello `even more code` World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("code World", TextType.CODE),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even more code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL)]
        self.assertEqual(split_nodes_delimiter(nodes, "`", TextType.CODE), expected)

    def test_split_nodes_delimiter_consequent(self):
        nodes = [TextNode("Hello `code` World", TextType.NORMAL),
                 TextNode("Hello `even` `more` `code` World", TextType.NORMAL)]
        expected = [TextNode("Hello ", TextType.NORMAL),
                    TextNode("code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL),
                    TextNode("Hello ", TextType.NORMAL),
                    TextNode("even", TextType.CODE),
                    TextNode("", TextType.NORMAL),
                    TextNode(" more", TextType.CODE),
                    TextNode("", TextType.NORMAL),
                    TextNode(" code", TextType.CODE),
                    TextNode(" World", TextType.NORMAL)]
        
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
        text = "This *is **text** with an italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        expected = [
            TextNode("This ", TextType.NORMAL),
            TextNode("is ", TextType.ITALIC),
            TextNode("text", TextType.BOLD),
            TextNode(" with an italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.NORMAL),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.NORMAL),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.NORMAL),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(text_to_textnodes(text), expected)
