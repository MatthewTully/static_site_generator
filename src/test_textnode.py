"""Unit test for text node."""
import unittest
from htmlnode import LeafNode
from textnode import TextNode, text_node_to_html_node

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        # is equal
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold")
        self.assertEqual(node, node2)

        # not equal, different text type
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "normal")
        self.assertNotEqual(node, node2)

        # not equal, different text
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a different text node", "bold")
        self.assertNotEqual(node, node2)

        # not equal, different text and text type
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a different text node", "normal")
        self.assertNotEqual(node, node2)

        # is equal with  1 url defined 
        node = TextNode("This is a text node", "bold", "test.com")
        node2 = TextNode("This is a text node", "bold")
        self.assertEqual(node, node2)

        # is equal with both url defined and same
        node = TextNode("This is a text node", "bold", "test.com")
        node2 = TextNode("This is a text node", "bold", "test.com")
        self.assertEqual(node, node2)

        # is equal with 1 url defined (other node)
        node = TextNode("This is a text node", "bold")
        node2 = TextNode("This is a text node", "bold", "text.com")
        self.assertEqual(node, node2)

        # is equal with both url defined, different
        node = TextNode("This is a text node", "bold", "test.com")
        node2 = TextNode("This is a text node", "bold", "text.com")
        self.assertEqual(node, node2)

    def test_repr(self):
        expected = "TextNode(Test text, test text type, url)"
        node = TextNode("Test text", "test text type", "url")
        self.assertEqual(expected, node.__repr__())

        expected = "TextNode(Test text, test text type, None)"
        node = TextNode("Test text", "test text type")
        self.assertEqual(expected, node.__repr__())

    def test_init_text_node(self):
        # all fields set.
        node = TextNode("text", "type", "url")
        self.assertEqual(node.text, "text")
        self.assertEqual(node.text_type, "type")
        self.assertEqual(node.url, "url")

        # url is optional
        node = TextNode("text", "type")
        self.assertEqual(node.text, "text")
        self.assertEqual(node.text_type, "type")
        self.assertIsNone(node.url)

class TestTextNodeToHTMLNode(unittest.TestCase):
    # test LeafNode response
    def test_is_leaf_node_response(self):
        test_node = TextNode("I am raw text", "text")
        self.assertIsInstance(text_node_to_html_node(test_node), LeafNode)

    # test each type
    def test_test_node_text(self):
        test_node = TextNode("I am raw text", "text")
        res_node = text_node_to_html_node(test_node)
        self.assertEqual(res_node.value, test_node.text)
        self.assertIsNone(res_node.tag)
        self.assertIsNone(res_node.children)
        self.assertIsNone(res_node.props)
    
    def test_test_node_bold(self):
        test_node = TextNode("I am bold text", "bold")
        res_node = text_node_to_html_node(test_node)
        self.assertEqual(res_node.value, test_node.text)
        self.assertEqual(res_node.tag, "b")
        self.assertIsNone(res_node.children)
        self.assertIsNone(res_node.props)

    def test_test_node_italic(self):
        test_node = TextNode("I am italic text", "italic")
        res_node = text_node_to_html_node(test_node)
        self.assertEqual(res_node.value, test_node.text)
        self.assertEqual(res_node.tag, "i")
        self.assertIsNone(res_node.children)
        self.assertIsNone(res_node.props)

    def test_test_node_code(self):
        test_node = TextNode("I am code text", "code")
        res_node = text_node_to_html_node(test_node)
        self.assertEqual(res_node.value, test_node.text)
        self.assertEqual(res_node.tag, "code")
        self.assertIsNone(res_node.children)
        self.assertIsNone(res_node.props)

    def test_test_node_link(self):
        test_node = TextNode("I am link text", "link", "www.fakeURL.com")
        res_node = text_node_to_html_node(test_node)
        self.assertEqual(res_node.value, test_node.text)
        self.assertEqual(res_node.tag, "a")
        self.assertIsNone(res_node.children)
        self.assertDictEqual(res_node.props, {"href": test_node.url})
    
    def test_test_node_link_no_url(self):
        test_node = TextNode("I am link text", "link")
        res_node = text_node_to_html_node(test_node)
        self.assertEqual(res_node.value, test_node.text)
        self.assertEqual(res_node.tag, "a")
        self.assertIsNone(res_node.children)
        self.assertDictEqual(res_node.props, {"href": None})

    def test_test_node_image(self):
        test_node = TextNode("I am alt text", "image", "www.fakeURL.com")
        res_node = text_node_to_html_node(test_node)
        self.assertEqual(res_node.value,"")
        self.assertEqual(res_node.tag, "img")
        self.assertIsNone(res_node.children)
        self.assertDictEqual(res_node.props, {"src": test_node.url, "alt": test_node.text})

    # test exception
    def test_test_node_text(self):
        test_node = TextNode("I am not expected", "I am raw text")
        with self.assertRaisesRegex(Exception, "Text type does not match expected types."):
            text_node_to_html_node(test_node)

if __name__ == "__main__":
    unittest.main()