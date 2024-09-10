"""Unit test main."""
import unittest
from main import split_nodes_delimiter, set_closing_delimiter, validate_delimiter_for_type, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, populate_html_node_for_block, strip_markdown_syntax, get_heading_count, populate_html_node_for_list_blocks, markdown_to_html, extract_title
from textnode import TextNode
from htmlnode import ParentNode

class TestSetClosingDelimiter(unittest.TestCase):
    def test_set_text(self):
        self.assertEqual(set_closing_delimiter("text"), "")
    def test_set_bold(self):
        self.assertEqual(set_closing_delimiter("bold"), "**")
    def test_set_italic(self):
        self.assertEqual(set_closing_delimiter("italic"), "*")
    def test_set_code(self):
        self.assertEqual(set_closing_delimiter("code"), "`")
    def test_set_link(self):
        self.assertEqual(set_closing_delimiter("link"), "]")
    def test_set_image(self):
        self.assertEqual(set_closing_delimiter("image"), "]")
    def test_raise_exception(self):
        with self.assertRaisesRegex(ValueError, "Invalid text type."):
            set_closing_delimiter("not_in_list")

class TestValidateDelimiterForType(unittest.TestCase):
    def test_all_valid(self):
        test_case = [
            ("text", ""),
            ("bold", "**"),
            ("italic", "*"),
            ("code", "`"),
            ("link", "["),
            ("image", "![")
        ]
        for test in test_case:
            text_type, delimiter = test
            self.assertTrue(validate_delimiter_for_type(delimiter, text_type))

    def test_raise_error(self):
        with self.assertRaisesRegex(ValueError, "Invalid delimiter for given text type."):
            validate_delimiter_for_type("**", "code")

class TestSplitNodeDelimiter(unittest.TestCase):
    def test_all_text(self):
        node = TextNode("I'm all text", "text")
        response = split_nodes_delimiter([node], "*", "italic")
        self.assertListEqual([node], response)

    def test_code_block(self):
        node = TextNode("This is text with a `code block` word", "text")
        response = split_nodes_delimiter([node], "`", "code")
        self.assertEqual(len(response), 3)
        self.assertEqual("This is text with a ", response[0].text)
        self.assertEqual("code block", response[1].text)
        self.assertEqual(" word", response[2].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("code", response[1].text_type)
        self.assertEqual("text", response[2].text_type)
    
    def test_bold_block(self):
        node = TextNode("This is text with a **bold block** word", "text")
        response = split_nodes_delimiter([node], "**", "bold")
        self.assertEqual(len(response), 3)
        self.assertEqual("This is text with a ", response[0].text)
        self.assertEqual("bold block", response[1].text)
        self.assertEqual(" word", response[2].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("bold", response[1].text_type)
        self.assertEqual("text", response[2].text_type)

    def test_bold_block_delimiter_with_italic(self):
        node = TextNode("This is text with a *italic block* word", "text")
        response = split_nodes_delimiter([node], "**", "bold")
        self.assertEqual(len(response), 1)
        self.assertListEqual([node], response)

        node = TextNode("This is text with a **bold block** and an *italic block* word", "text")
        response = split_nodes_delimiter([node], "**", "bold")
        self.assertEqual(len(response), 3)
        self.assertEqual("This is text with a ", response[0].text)
        self.assertEqual("bold block", response[1].text)
        self.assertEqual(" and an *italic block* word", response[2].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("bold", response[1].text_type)
        self.assertEqual("text", response[2].text_type)

    def test_italic_block(self):
        node = TextNode("This is text with a *italic block* word", "text")
        response = split_nodes_delimiter([node], "*", "italic")
        self.assertEqual(len(response), 3)
        self.assertEqual("This is text with a ", response[0].text)
        self.assertEqual("italic block", response[1].text)
        self.assertEqual(" word", response[2].text)
        self.assertEqual("text", response[0].text_type)
        self.assertEqual("italic", response[1].text_type)
        self.assertEqual("text", response[2].text_type)

        node = TextNode("This is text with a *italic block* word and *another one* too" , "text")
        response = split_nodes_delimiter([node], "*", "italic")
        self.assertEqual(len(response), 5)
        self.assertEqual("This is text with a ", response[0].text)
        self.assertEqual("italic block", response[1].text)
        self.assertEqual(" word and ", response[2].text)
        self.assertEqual("another one", response[3].text)
        self.assertEqual(" too", response[4].text)
        self.assertEqual("text", response[0].text_type)
        self.assertEqual("italic", response[1].text_type)
        self.assertEqual("text", response[2].text_type)
        self.assertEqual("italic", response[3].text_type)
        self.assertEqual("text", response[4].text_type)

    def test_italic_block_delimiter_with_bold(self):
        node = TextNode("This is text with a **bold block** word", "text")
        response = split_nodes_delimiter([node], "*", "italic")
        self.assertEqual(len(response), 1)
        self.assertListEqual([node], response)

        node = TextNode("This is text with a **bold block** and a *italic block* word", "text")
        response = split_nodes_delimiter([node], "*", "italic")
        self.assertEqual(len(response), 3)
        self.assertEqual("This is text with a **bold block** and a ", response[0].text)
        self.assertEqual("italic block", response[1].text)
        self.assertEqual(" word", response[2].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("italic", response[1].text_type)
        self.assertEqual("text", response[2].text_type)

class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_image(self):
        text = "This block includes an image.. ![I'm alt text](image.jpg) before here!"
        expected = [("I'm alt text", "image.jpg")]
        response = extract_markdown_images(text)
        self.assertListEqual(response, expected)
        self.assertEqual("I'm alt text", response[0][0])
        self.assertEqual("image.jpg", response[0][1])
    
    def test_extract_image_multiple(self):
        text = "This block includes an image.. ![I'm alt text](image.jpg) before here! and another: ![I'm alt text too](image2.jpg)"
        expected = [("I'm alt text", "image.jpg"),("I'm alt text too", "image2.jpg")]
        response = extract_markdown_images(text)
        self.assertListEqual(response, expected)
        self.assertEqual("I'm alt text", response[0][0])
        self.assertEqual("image.jpg", response[0][1])
        self.assertEqual("I'm alt text too", response[1][0])
        self.assertEqual("image2.jpg", response[1][1])
    
    def test_extract_image_with_link(self):
        text = "This block includes an image.. ![I'm alt text](image.jpg) before here! plus a link.. [I'm a link](www.linkedUrl.com)"
        expected = [("I'm alt text", "image.jpg")]
        response = extract_markdown_images(text)
        self.assertListEqual(response, expected)
        self.assertEqual("I'm alt text", response[0][0])
        self.assertEqual("image.jpg", response[0][1])
        
class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_link(self):
        text = "This block includes a link.. [I'm a link](www.linkedUrl.com) before here!"
        expected = [("I'm a link", "www.linkedUrl.com")]
        response = extract_markdown_links(text)
        self.assertListEqual(response, expected)
        self.assertEqual("I'm a link", response[0][0])
        self.assertEqual("www.linkedUrl.com", response[0][1])
    
    def test_extract_link_multiple(self):
        text = "This block includes a link.. [I'm a link](www.linkedUrl.com) before here! and another: [I'm also a link](www.linkedUrl2.com)"
        expected = [("I'm a link", "www.linkedUrl.com"),("I'm also a link", "www.linkedUrl2.com")]
        response = extract_markdown_links(text)
        self.assertListEqual(response, expected)
        self.assertEqual("I'm a link", response[0][0])
        self.assertEqual("www.linkedUrl.com", response[0][1])
        self.assertEqual("I'm also a link", response[1][0])
        self.assertEqual("www.linkedUrl2.com", response[1][1])

    def test_extract_link_with_image(self):
        text = "This block includes a link.. [I'm a link](www.linkedUrl.com) before here! and an image: ![I'm alt text too](image2.jpg)"
        expected = [("I'm a link", "www.linkedUrl.com")]
        response = extract_markdown_links(text)
        self.assertListEqual(response, expected)
        self.assertEqual("I'm a link", response[0][0])
        self.assertEqual("www.linkedUrl.com", response[0][1])

class TestSplitNodeLink(unittest.TestCase):
    def test_all_text(self):
        node = TextNode("I'm all text", "text")
        response = split_nodes_link([node])
        self.assertListEqual([node], response)

    def test_node_with_link(self):
        node = TextNode("This block includes a link.. [I'm a link](www.linkedUrl.com) before here!", "text")
        response = split_nodes_link([node])
        self.assertEqual(len(response), 3)
        self.assertEqual("This block includes a link.. ", response[0].text)
        self.assertEqual("I'm a link", response[1].text)
        self.assertEqual("www.linkedUrl.com", response[1].url)
        self.assertEqual(" before here!", response[2].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("link", response[1].text_type)
        self.assertEqual("text", response[2].text_type)

    def test_node_with_2_links(self):
        node = TextNode("This block includes a link.. [I'm a link](www.linkedUrl.com) before here! and another: [I'm also a link](www.linkedUrl2.com)", "text")
        response = split_nodes_link([node])
        self.assertEqual(len(response), 4)
        self.assertEqual("This block includes a link.. ", response[0].text)
        self.assertEqual("I'm a link", response[1].text)
        self.assertEqual("www.linkedUrl.com", response[1].url)
        self.assertEqual(" before here! and another: ", response[2].text)
        self.assertEqual("I'm also a link", response[3].text)
        self.assertEqual("www.linkedUrl2.com", response[3].url)
        

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("link", response[1].text_type)
        self.assertEqual("text", response[2].text_type)
        self.assertEqual("link", response[3].text_type)

    def test_node_with_link_and_image(self):
        node = TextNode("This block includes a link.. [I'm a link](www.linkedUrl.com) before here! and an image: ![I'm alt text too](image2.jpg)", "text")
        response = split_nodes_link([node])
        self.assertEqual(len(response), 3)
        self.assertEqual("This block includes a link.. ", response[0].text)
        self.assertEqual("I'm a link", response[1].text)
        self.assertEqual("www.linkedUrl.com", response[1].url)
        self.assertEqual(" before here! and an image: ![I'm alt text too](image2.jpg)", response[2].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("link", response[1].text_type)
        self.assertEqual("text", response[2].text_type)

    
    def test_node_with_multiple_node_in(self):
        node_list = [
            TextNode("This block includes a link.. [I'm a link](www.linkedUrl.com) before here!", "text"),
            TextNode(" I'm all text", "text"),
            TextNode("This block includes a link.. [I'm a link](www.linkedUrl.com) before here! and an image: ![I'm alt text too](image2.jpg)", "text"),
            TextNode(" I'm all text", "text")
        ]
        response = split_nodes_link(node_list)
        self.assertEqual(len(response), 8)
        self.assertEqual("This block includes a link.. ", response[0].text)
        self.assertEqual("I'm a link", response[1].text)
        self.assertEqual("www.linkedUrl.com", response[1].url)
        self.assertEqual(" before here!", response[2].text)
        self.assertEqual(" I'm all text", response[3].text)
        self.assertEqual("This block includes a link.. ", response[4].text)
        self.assertEqual("I'm a link", response[5].text)
        self.assertEqual("www.linkedUrl.com", response[5].url)
        self.assertEqual(" before here! and an image: ![I'm alt text too](image2.jpg)", response[6].text)
        self.assertEqual(" I'm all text", response[7].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("link", response[1].text_type)
        self.assertEqual("text", response[2].text_type)
        self.assertEqual("text", response[3].text_type)
        self.assertEqual("text", response[4].text_type)
        self.assertEqual("link", response[5].text_type)
        self.assertEqual("text", response[6].text_type)
        self.assertEqual("text", response[7].text_type)

class TestSplitNodeImage(unittest.TestCase):
    def test_all_text(self):
        node = TextNode("I'm all text", "text")
        response = split_nodes_image([node])
        self.assertListEqual([node], response)

    def test_node_with_image(self):
        node = TextNode("This block includes an image.. ![I'm alt text](image.jpg) before here!", "text")
        response = split_nodes_image([node])
        self.assertEqual(len(response), 3)
        self.assertEqual("This block includes an image.. ", response[0].text)
        self.assertEqual("I'm alt text", response[1].text)
        self.assertEqual("image.jpg", response[1].url)
        self.assertEqual(" before here!", response[2].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("image", response[1].text_type)
        self.assertEqual("text", response[2].text_type)

    def test_node_with_2_images(self):
        node = TextNode("This block includes an image.. ![I'm alt text](image.jpg) before here! and another: ![I'm alt text too](image2.jpg)", "text")
        response = split_nodes_image([node])
        self.assertEqual(len(response), 4)
        self.assertEqual("This block includes an image.. ", response[0].text)
        self.assertEqual("I'm alt text", response[1].text)
        self.assertEqual("image.jpg", response[1].url)
        self.assertEqual(" before here! and another: ", response[2].text)
        self.assertEqual("I'm alt text too", response[3].text)
        self.assertEqual("image2.jpg", response[3].url)
        

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("image", response[1].text_type)
        self.assertEqual("text", response[2].text_type)
        self.assertEqual("image", response[3].text_type)

    def test_node_with_image_and_link(self):
        node = TextNode("This block includes an image.. ![I'm alt text](image.jpg) before here! plus a link.. [I'm a link](www.linkedUrl.com)", "text")
        response = split_nodes_image([node])
        self.assertEqual(len(response), 3)
        self.assertEqual("This block includes an image.. ", response[0].text)
        self.assertEqual("I'm alt text", response[1].text)
        self.assertEqual("image.jpg", response[1].url)
        self.assertEqual(" before here! plus a link.. [I'm a link](www.linkedUrl.com)", response[2].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("image", response[1].text_type)
        self.assertEqual("text", response[2].text_type)

    def test_node_with_multiple_node_in(self):
        node_list = [
            TextNode("This block includes an image.. ![I'm alt text](image.jpg) before here!", "text"),
            TextNode(" I'm all text", "text"),
            TextNode("This block includes an image.. ![I'm alt text](image.jpg) before here! plus a link.. [I'm a link](www.linkedUrl.com)", "text"),
            TextNode(" I'm all text", "text")
        ]
        response = split_nodes_image(node_list)
        self.assertEqual(len(response), 8)
        self.assertEqual("This block includes an image.. ", response[0].text)
        self.assertEqual("I'm alt text", response[1].text)
        self.assertEqual("image.jpg", response[1].url)
        self.assertEqual(" before here!", response[2].text)
        self.assertEqual(" I'm all text", response[3].text)
        self.assertEqual("This block includes an image.. ", response[4].text)
        self.assertEqual("I'm alt text", response[5].text)
        self.assertEqual("image.jpg", response[5].url)
        self.assertEqual(" before here! plus a link.. [I'm a link](www.linkedUrl.com)", response[6].text)
        self.assertEqual(" I'm all text", response[7].text)

        self.assertEqual("text", response[0].text_type)
        self.assertEqual("image", response[1].text_type)
        self.assertEqual("text", response[2].text_type)
        self.assertEqual("text", response[3].text_type)
        self.assertEqual("text", response[4].text_type)
        self.assertEqual("image", response[5].text_type)
        self.assertEqual("text", response[6].text_type)
        self.assertEqual("text", response[7].text_type)


class TestTextToTextNode(unittest.TestCase):
    def test_just_text(self):
        test_text = "I'm just text"
        res = text_to_textnodes(test_text)
        self.assertListEqual(res, [TextNode(test_text, "text")])

    def test_full_set(self):
        test_text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        expected = [
            TextNode("This is ", "text"),
            TextNode("text", "bold"),
            TextNode(" with an ", "text"),
            TextNode("italic", "italic"),
            TextNode(" word and a ", "text"),
            TextNode("code block", "code"),
            TextNode(" and an ", "text"),
            TextNode("obi wan image", "image", "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", "text"),
            TextNode("link", "link", "https://boot.dev")
        ]
        res = text_to_textnodes(test_text)
        self.assertListEqual(res, expected)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_header_and_paragraph(self):
        text = """# Welcome, I am **a bold header**!

This is a bit of a paragraph.
It got some **bold**, some *italic*.
Nothing too fancy.
        """
        expected = [
            "# Welcome, I am **a bold header**!",
            "This is a bit of a paragraph.\nIt got some **bold**, some *italic*.\nNothing too fancy."
        ]

        res = markdown_to_blocks(text)
        self. assertListEqual(expected, res)

    def test_2_blocks(self):
        text = """block1 - body body

        block2 - body body"""
        expected = [
            "block1 - body body",
            "block2 - body body"
        ]
        res = markdown_to_blocks(text)
        self. assertListEqual(expected, res)
    
    def test_1_block(self):
        text = "block-text"
        self.assertListEqual([text], markdown_to_blocks(text))
    
    def test_multi_line_block(self):
        text = """
# Heading 1

1. list
2. block

> quote
"""
        expected = [
            "# Heading 1",
            "1. list\n2. block",
            "> quote"
        ]
        res = markdown_to_blocks(text)
        self. assertListEqual(expected, res)

    def test_3_blocks_scrap_empty_lines_and_whitespace(self):
        text = """
block 1 - sdsdgsgsogjegjsg


block 2 - opdrojbdjrbpdr    



block 3 - irgsiogsoiengs


"""
        expected = ["block 1 - sdsdgsgsogjegjsg",
                    "block 2 - opdrojbdjrbpdr",
                    "block 3 - irgsiogsoiengs"]
        self.assertListEqual(markdown_to_blocks(text), expected)

class TestBlockToBlockType(unittest.TestCase):
    def test_is_paragraph(self):
        text_block = "this is text block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
    
    def test_is_heading(self):
        text_block = "# this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"heading")
        text_block = "## this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"heading")
        text_block = "### this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"heading")
        text_block = "#### this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"heading")
        text_block = "##### this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"heading")
        text_block = "###### this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"heading")

    def test_is_malformed_heading(self):
        text_block = "#this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
        text_block = "##this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
        text_block = "###this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
        text_block = "####this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
        text_block = "#####this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
        text_block = "######this is a heading block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
    
    def test_is_code(self):
        text_block = "```this is code block```"
        self.assertEqual(block_to_block_type(text_block) ,"code")

    def test_is_malformed_code(self):
        text_block = "```this is code block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
        text_block = "```this is code block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
    
    def test_is_quote(self):
        text_block = "> this is quote block"
        self.assertEqual(block_to_block_type(text_block) ,"quote")

    def test_is_unordered_list(self):
        text_block = "* this is unordered block starting with *"
        self.assertEqual(block_to_block_type(text_block) ,"unordered_list")
        
        text_block = "- this is unordered block starting with -"
        self.assertEqual(block_to_block_type(text_block) ,"unordered_list")
    
    def test_is_malformed_unordered_list(self):
        text_block = "*this is unordered block starting with *"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")
        
        text_block = "-this is unordered block starting with -"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")

    def test_is_ordered_list(self):
        text_block = "1. this is ordered list block"
        self.assertEqual(block_to_block_type(text_block) ,"ordered_list")
    
    def test_is_malformed_ordered_list(self):
        text_block = "A. this is text block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")

        text_block = "1.this is ordered list block"
        self.assertEqual(block_to_block_type(text_block) ,"paragraph")

class TestStripMarkdownSyntax(unittest.TestCase):
    def test_paragraph(self):
        test_str = "test text"
        self.assertEqual(test_str, strip_markdown_syntax(test_str, "paragraph"))

    def test_heading(self):
        test_str = "# test text"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "heading"))

        test_str = "## test text"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "heading"))

        test_str = "### test text"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "heading"))

        test_str = "#### test text"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "heading"))

        test_str = "##### test text"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "heading"))

        test_str = "###### test text"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "heading"))

    def test_code(self):
        test_str = "```test text```"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "code"))

    def test_ordered_list(self):
        test_str = "1. test text"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "ordered_list"))
    
    def test_unordered_list(self):
        test_str = "* test text"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "unordered_list"))
        test_str = "- test text"
        expect = "test text"
        self.assertEqual(expect, strip_markdown_syntax(test_str, "unordered_list"))

class TestGetHeadingCount(unittest.TestCase):
    def test_get_heading(self):
        test_str = "# test text"
        self.assertEqual(1, get_heading_count(test_str))

        test_str = "## test text"
        self.assertEqual(2, get_heading_count(test_str))

        test_str = "### test text"
        self.assertEqual(3, get_heading_count(test_str))

        test_str = "#### test text"
        self.assertEqual(4, get_heading_count(test_str))

        test_str = "##### test text"
        self.assertEqual(5, get_heading_count(test_str))

        test_str = "###### test text"
        self.assertEqual(6, get_heading_count(test_str))

class TestPopulateHTMLNodeForListBlocks(unittest.TestCase):
    def test_ordered_list(self):
        block_text = "1. item\n2. in\n3. a\n4. Ordered\n5. List"
        expected_html = "<ol><li>item</li><li>in</li><li>a</li><li>Ordered</li><li>List</li></ol>"
        res = populate_html_node_for_list_blocks("ordered_list", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

    def test_unordered_list(self):
        block_text = "- item\n- in\n- a\n- Unordered\n- List"
        expected_html = "<ul><li>item</li><li>in</li><li>a</li><li>Unordered</li><li>List</li></ul>"
        res = populate_html_node_for_list_blocks("unordered_list", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

        block_text = "* item\n* in\n* a\n* Unordered\n* List"
        expected_html = "<ul><li>item</li><li>in</li><li>a</li><li>Unordered</li><li>List</li></ul>"
        res = populate_html_node_for_list_blocks("unordered_list", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

class TestPopulateHTMLNodeForBlock(unittest.TestCase):
    def test_paragraph_block(self):
        block_text = "This is a block of text.\nIt does include some **bold**, and a bit of *italic*\nJust on that line though."
        expected_html = "<p>This is a block of text.\nIt does include some <b>bold</b>, and a bit of <i>italic</i>\nJust on that line though.</p>"
        res = populate_html_node_for_block("paragraph", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())
    
    def test_heading_block(self):
        block_text = "# This should be h1 heading."
        expected_html = "<h1>This should be h1 heading.</h1>"
        res = populate_html_node_for_block("heading", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

        block_text = "## This should be h2 heading."
        expected_html = "<h2>This should be h2 heading.</h2>"
        res = populate_html_node_for_block("heading", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

        block_text = "### This should be h3 heading."
        expected_html = "<h3>This should be h3 heading.</h3>"
        res = populate_html_node_for_block("heading", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

        block_text = "#### This should be h4 heading."
        expected_html = "<h4>This should be h4 heading.</h4>"
        res = populate_html_node_for_block("heading", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

        block_text = "##### This should be h5 heading."
        expected_html = "<h5>This should be h5 heading.</h5>"
        res = populate_html_node_for_block("heading", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

        block_text = "###### This should be h6 heading."
        expected_html = "<h6>This should be h6 heading.</h6>"
        res = populate_html_node_for_block("heading", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())
    
    def test_code_block(self):
        block_text = "```This is a block of code.\nIt does include some **bold**, and a bit of *italic*\nJust on that line though.```"
        expected_html = "<pre><code>This is a block of code.\nIt does include some <b>bold</b>, and a bit of <i>italic</i>\nJust on that line though.</code></pre>"
        res = populate_html_node_for_block("code", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

    def test_quote_block(self):
        block_text = ">This is a block of text.\n>It does include some **bold**, and a bit of *italic*\n>Just on that line though."
        expected_html = "<blockquote>This is a block of text.\nIt does include some <b>bold</b>, and a bit of <i>italic</i>\nJust on that line though.</blockquote>"
        res = populate_html_node_for_block("quote", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

    def test_ordered_block(self):
        block_text = "1. *item*\n2. in\n3. a\n4. **Ordered**\n5. List"
        expected_html = "<ol><li><i>item</i></li><li>in</li><li>a</li><li><b>Ordered</b></li><li>List</li></ol>"
        res = populate_html_node_for_block("ordered_list", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

    def test_unordered_block(self):
        block_text = "- item\n- in\n- a\n- **Un**ordered\n- List"
        expected_html = "<ul><li>item</li><li>in</li><li>a</li><li><b>Un</b>ordered</li><li>List</li></ul>"
        res = populate_html_node_for_block("unordered_list", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

        block_text = "* item\n* in\n* a\n* Unordered\n* List"
        expected_html = "<ul><li>item</li><li>in</li><li>a</li><li>Unordered</li><li>List</li></ul>"
        res = populate_html_node_for_block("unordered_list", block_text)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())

class TestMarkdownToHTML(unittest.TestCase):
    def test_header_paragraph_list_paragraph(self):
        markdown_block="""# Welcome, I am **a bold header**!

This is a bit of a paragraph.
It got some **bold**, some *italic*.
Nothing too fancy.

1. It does have a list
2. Of things
3. listing nothing.

And another paragraph, but this one has a link on the next line.
[I'm a link](www.linkedUrl.com)

```Finish with a code block?```

>Nope, its a quote block... with some `code in it`, and that's it."""
        expected_html="<div><h1>Welcome, I am <b>a bold header</b>!</h1><p>This is a bit of a paragraph.\nIt got some <b>bold</b>, some <i>italic</i>.\nNothing too fancy.</p><ol><li>It does have a list</li><li>Of things</li><li>listing nothing.</li></ol><p>And another paragraph, but this one has a link on the next line.\n<a href=\"www.linkedUrl.com\">I'm a link</a></p><pre><code>Finish with a code block?</code></pre><blockquote>Nope, its a quote block... with some <code>code in it</code>, and that's it.</blockquote></div>"
        res = markdown_to_html(markdown_block)
        self.assertIsInstance(res, ParentNode)
        self.assertEqual(expected_html, res.to_html())


class TestExtractTitle(unittest.TestCase):
    def test_happy_path(self):
        self.assertEqual("This is a title.", extract_title("# This is a title."))

        test_str = """# I am a title           """
        expected = "I am a title"
        self.assertEqual(expected, extract_title(test_str))

        test_str = """# I am a title
This is not,
Neither is this.            """
        expected = "I am a title"
        self.assertEqual(expected, extract_title(test_str))

    def test_exception(self):
        with self.assertRaisesRegex(Exception, "No Header found in text."):
            extract_title("")

        with self.assertRaisesRegex(Exception, "No Header found in text."):
            extract_title("I am not a title")

        with self.assertRaisesRegex(Exception, "No Header found in text."):
            test_str = """I am not a title
This is not,
Neither is this.            """
            extract_title(test_str)