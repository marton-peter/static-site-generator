import unittest
from main import text_node_to_html_node
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