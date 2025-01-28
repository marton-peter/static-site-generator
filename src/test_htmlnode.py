import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode(tag="p", value="This is an HTML node", children=None, props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        node2 = HTMLNode(tag="p", value="This is an HTML node", children=None, props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = HTMLNode(tag="p", value="This is an HTML node", children=None, props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        node2 = HTMLNode(tag="p", value="This is another HTML node", children=None, props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        self.assertNotEqual(node, node2)

    def test_props_to_html_eq(self):
        node = HTMLNode(tag="p", value="This is an HTML node", children=None, props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        node2 = HTMLNode(tag="p", value="This is an HTML node", children=None, props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        self.assertEqual(node.props_to_html(), node2.props_to_html())

    def test_props_to_html_not_eq(self):
        node = HTMLNode(tag="p", value="This is an HTML node", children=None, props={
        "href": "https://www.google.com"
        } )
        node2 = HTMLNode(tag="p", value="This is an HTML node", children=None, props={
        "href": "https://www.google.com",
        "target": "_blank",
        } )
        self.assertNotEqual(node.props_to_html(), node2.props_to_html())