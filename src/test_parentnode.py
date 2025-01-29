import unittest

from htmlnode import HTMLNode
from parentnode import ParentNode
from leafnode import LeafNode

class TestParentNode(unittest.TestCase):
    def test_repr(self):
        node = ParentNode(
        "p",
        [
        LeafNode("b", "Bold text"),
        LeafNode(None, "Normal text"),
        LeafNode("i", "italic text"),
        LeafNode(None, "Normal text"),
        ],)

        expected = "ParentNode(tag='p', children=[LeafNode(tag='b', value='Bold text', props=None), LeafNode(tag=None, value='Normal text', props=None), LeafNode(tag='i', value='italic text', props=None), LeafNode(tag=None, value='Normal text', props=None)], props=None)"
        
        self.assertEqual(repr(node), expected)

    def test_notag(self):
        node = ParentNode(
        "",
        [
        LeafNode("b", "Bold text"),
        LeafNode(None, "Normal text"),
        LeafNode("i", "italic text"),
        LeafNode(None, "Normal text"),
        ],)

        with self.assertRaises(ValueError) as context:
            node.to_html()
        self.assertEqual(str(context.exception), "Missing tag")

    def test_nochildren(self):
        node = ParentNode("p", [],)

        with self.assertRaises(ValueError) as context:
                node.to_html()
        self.assertEqual(str(context.exception), "No children")

    def test_props(self):
        node = ParentNode(
        "p",
        [
        LeafNode("b", "Bold text"),
        LeafNode(None, "Normal text"),
        LeafNode("i", "italic text"),
        LeafNode(None, "Normal text"),
        ],
        props={
        "href": "https://www.google.com",
        "target": "_blank",
        })

        expected = "ParentNode(tag='p', children=[LeafNode(tag='b', value='Bold text', props=None), LeafNode(tag=None, value='Normal text', props=None), LeafNode(tag='i', value='italic text', props=None), LeafNode(tag=None, value='Normal text', props=None)], props={'href': 'https://www.google.com', 'target': '_blank'})"
        
        self.assertEqual(repr(node), expected)
