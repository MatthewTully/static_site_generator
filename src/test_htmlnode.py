"""Unit test for html node."""
import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_init(self):
        # all fields optional.
        node1 = HTMLNode()
        self.assertIsNone(node1.tag)
        self.assertIsNone(node1.value)
        self.assertIsNone(node1.children)
        self.assertIsNone(node1.props)

        # all set.
        node2 = HTMLNode("p", "test_val", [node1], {"href": "https://test.co.test"})
        self.assertEqual(node2.tag, "p")
        self.assertEqual(node2.value, "test_val")
        self.assertListEqual(node2.children, [node1])
        self.assertDictEqual(node2.props, {"href": "https://test.co.test"})

    def test_to_html(self):
        # throws error
        node = HTMLNode()
        self.assertRaises(NotImplementedError, node.to_html)

    def test_repr(self):
        expected = "HTMLNode(tag, val, [], {'a': 'b'})"
        node = HTMLNode("tag", "val", [], {"a":"b"})
        self.assertEqual(expected, node.__repr__())

    def test_props_to_html(self):
        # No props
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

        # 1 prop
        node = HTMLNode(props={"test":"value"})
        self.assertEqual(node.props_to_html(), 'test="value"')

        # 2 prop
        node = HTMLNode(props={"test":"value", "prop-b": "prop-b value"})
        self.assertEqual(node.props_to_html(), 'test="value" prop-b="prop-b value"')


class TestLeafNode(unittest.TestCase):
    def test_init(self):
        # all fields optional except value.
        self.assertRaises(TypeError, LeafNode)
 
        # all set.
        node = LeafNode(tag="p", value="test_val", props={"href": "https://test.co.test"})
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "test_val")
        self.assertIsNone(node.children)
        self.assertDictEqual(node.props, {"href": "https://test.co.test"})

    def test_to_html(self):
        # no value throws error
        node = LeafNode(tag=None, value="value")
        node.value = None
        self.assertRaises(ValueError, node.to_html)

        # no tag, raw text
        node = LeafNode(tag=None, value="value")
        self.assertEqual(node.to_html(), "value")

        # p tag
        node= LeafNode(tag="p", value="I am a value")
        self.assertEqual(node.to_html(), "<p>I am a value</p>")

        # props
        node= LeafNode(tag="p", value="I am a value", props={"href": "https://test.com"})
        self.assertEqual(node.to_html(), '<p href="https://test.com">I am a value</p>')

    def test_repr(self):
        expected = "LeafNode(tag, val, {'a': 'b'})"
        node = LeafNode(tag="tag", value="val", props={"a":"b"})
        self.assertEqual(expected, node.__repr__())

    def test_props_to_html(self):
        # No props
        node = LeafNode(tag=None, value="value")
        self.assertEqual(node.props_to_html(), "")

        # 1 prop
        node = LeafNode(tag=None, value="value", props={"test":"value"})
        self.assertEqual(node.props_to_html(), 'test="value"')

        # 2 prop
        node = LeafNode(tag=None, value="value", props={"test":"value", "prop-b": "prop-b value"})
        self.assertEqual(node.props_to_html(), 'test="value" prop-b="prop-b value"')


class TestParentNode(unittest.TestCase):
    def test_init(self):
        # all fields optional except value.
        self.assertRaises(TypeError, ParentNode)
 
        # all set.
        node = ParentNode(tag="p", children=[], props={"href": "https://test.co.test"})
        self.assertEqual(node.tag, "p")
        self.assertListEqual(node.children,[])
        self.assertIsNone(node.value)
        self.assertDictEqual(node.props, {"href": "https://test.co.test"})

    def test_to_html(self):
        # no tag throws error
        with self.assertRaisesRegex(ValueError, "Tag has not been set."):
            node = ParentNode(tag=None, children=[])
            node.to_html()

        # no children throws error
        with self.assertRaisesRegex(ValueError, "Expected Children."):
            node = ParentNode(tag="div", children=[])
            node.to_html()

        with self.assertRaisesRegex(ValueError, "Expected Children."):
            node = ParentNode(tag="div", children=None)
            node.to_html()

        # All children, mix with and without props/tag
        children = [
            LeafNode("p", "I am a paragraph", {"href": "www.test.com"}),
            LeafNode("p", "I am also a paragraph"),
            LeafNode(None, "I am a raw"),
        ]
        node = ParentNode("div", children, {"href":"parentProp"})
        self.assertEqual(node.to_html(), '<div href="parentProp"><p href="www.test.com">I am a paragraph</p><p>I am also a paragraph</p>I am a raw</div>')
        
        # All parent - no children
        children = [
            ParentNode("p", [], {"href": "www.test.com"}),
            ParentNode("p", [])
        ]
        node = ParentNode("div", children, {"href":"parentProp"})
        with self.assertRaisesRegex(ValueError, "Expected Children."):
            node.to_html()
        
        # All parent - with a child
        children = [
            ParentNode("div", [LeafNode("p", "I am a child paragraph")], {"href": "www.test.com"}),
            ParentNode("div", [LeafNode(None, "RAW"),])
        ]
        node = ParentNode("div", children, {"href":"parentProp"})
        self.assertEqual(node.to_html(), '<div href="parentProp"><div href="www.test.com"><p>I am a child paragraph</p></div><div>RAW</div></div>')
        
        # some parent with some children
        children = [
            LeafNode("p", "I am a paragraph", {"href": "www.test.com"}),
            ParentNode("div", [LeafNode("p", "I am a child paragraph")], {"href": "www.test.com"}),
            LeafNode("p", "I am also a paragraph"),
            ParentNode("div", [LeafNode("p", "I am also a child paragraph", {"diff":"I have a prop"})]),
            LeafNode(None, "I am a raw"),
        ]
        node = ParentNode("div", children)
        self.assertEqual(node.to_html(), '<div><p href="www.test.com">I am a paragraph</p><div href="www.test.com"><p>I am a child paragraph</p></div><p>I am also a paragraph</p><div><p diff="I have a prop">I am also a child paragraph</p></div>I am a raw</div>')

    def test_repr(self):
        expected = "ParentNode(tag, [], {'a': 'b'})"
        node = ParentNode(tag="tag", children=[], props={"a":"b"})
        self.assertEqual(expected, node.__repr__())