import unittest

from leafnode import LeafNode

class TestLeafNode(unittest.TestCase):
    def test_eq(self):
        node = LeafNode(tag="p", value="This is an HTML node", props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        node2 = LeafNode(tag="p", value="This is an HTML node", props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        self.assertEqual(node, node2)

    def test_repr(self):
        node = LeafNode(tag="p", value="This is an HTML node", props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        expected = "LeafNode(tag='p', value='This is an HTML node', props={'href': 'https://www.google.com', 'target': '_blank'})"
        self.assertEqual(repr(node), expected)

    def test_missing_tag(self):
        node = LeafNode(tag=None, value="Just plain text")
        self.assertEqual(node.to_html(), "Just plain text")

    def test_missing_props(self):
        node = LeafNode(tag=None, value="Just plain text", props=None)
        self.assertEqual(node.to_html(), "Just plain text")

    def test_missing_value(self):
        node = LeafNode(tag="p", value="")
        with self.assertRaises(ValueError):
            node.to_html()

    def test_none_value(self):
        node = LeafNode(tag="p", value=None)
        with self.assertRaises(ValueError):
            node.to_html()