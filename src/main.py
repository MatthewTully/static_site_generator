"""Entry point for main."""
from textnode import TextNode, text_node_to_html_node
from htmlnode import ParentNode
import re
import os
import shutil

text_type_text = ("text", "")
text_type_bold = ("bold", "**")
text_type_italic = ("italic", "*")
text_type_code = ("code", "`")
text_type_link = ("link", "[", "]")
text_type_image = ("image", "![", "]")

def main() -> None:
    """main func."""
    copy_files("./static", "./public")
    generate_pages_recursive("./content", "./template.html", "./public")

def copy_files(source:str, destination:str, destination_root:str|None=None) -> None:
    """Recursively copy files from source to destination."""
    print(f"Copying from {source} to {destination}")
    if destination_root is None:
        destination_root = destination
        if os.path.exists(destination_root):
            print(f"cleaning destination first!")
            print(f"list of destination pre clean: {os.listdir(destination)}")
            shutil.rmtree(destination)
        os.mkdir(destination)        
    if not os.path.exists(source):
        print("Source does not exists")
        raise Exception("Source does not exist.")
    
    # loop over it in source, if file copy to destination, if dir, call self.
    for item in os.listdir(source):
        item_path = os.path.join(source, item)
        if os.path.isfile(item_path):
            print(f"{item} is a file, copying...")
            shutil.copy(item_path, destination)
            if os.path.exists(os.path.join(destination, item)):
                print(f"{item} successfully copied.")
            else:
                print(f"Error {item} failed to copy.")
        else:
            print(f"{item} is a dir, create and copy content...")
            os.mkdir(os.path.join(destination, item))
            copy_files(item_path, os.path.join(destination, item), destination)
            print(f"{item} created and populated.")
    if destination == destination_root:
        print("Copy successful")
    return


def output_html(to_path:str, html:str) -> None:
    """Output HTML to file."""
    print(f"Outputting HTML file to {to_path}")
    with open(os.path.join(to_path), 'w', encoding="utf-8") as output:
        output.write(html)
        output.close

def generate_pages_recursive(dir_path_content:str, template_path:str, dest_dir_path:str) -> None:
    """Recursively generate markdown pages."""
    if not os.path.exists(dest_dir_path):
        print(f"{dest_dir_path} does not exist, creating..")
        os.mkdir(dest_dir_path)

    for item in os.listdir(dir_path_content):
        item_path = os.path.join(dir_path_content, item)
        if os.path.isfile(item_path):
            print(f"generating {item}")
            new_file_name = f"{item.split('.')[0]}.html"
            generate_page(item_path, template_path, os.path.join(dest_dir_path, new_file_name))
        else:
            generate_pages_recursive(item_path, template_path, os.path.join(dest_dir_path, item))


def generate_page(from_path:str, template_path:str, dest_path:str) -> None:
    """Generate HTML from template and markdown."""
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown = None
    template = None
    with open(from_path, 'r', encoding="utf-8") as from_file:
        markdown = from_file.read()
        from_file.close()
    if markdown is None:
        raise Exception(f"Failed to read content from {from_path}")
    with open(template_path, 'r', encoding="utf-8") as template_file:
        template = template_file.read()
        template_file.close()
    if template is None:
        raise Exception(f"Failed to read content from {from_path}")
    html = markdown_to_html(markdown).to_html()
    title = extract_title(markdown)

    new_html = template.replace("{{ Title }}", title).replace("{{ Content }}", html)
    output_html(dest_path, new_html)


def extract_title(markdown: str) -> str:
    """Extract H1 header from markdown."""
    lines = markdown.split("\n")
    header_list = list(filter(lambda x: x.startswith("# "), lines))
    if len(header_list) == 0:
        raise Exception("No Header found in text.")
    return header_list[0][2:].strip()


def strip_markdown_syntax(string_to_strip:str, block_type:str):
    """Strips markdown syntax from blocks."""
    if block_type == "paragraph":
        return string_to_strip.strip()
    if block_type == "heading":
        return string_to_strip[get_heading_count(string_to_strip)+1:].strip()
    if block_type == "code":
        return string_to_strip.removeprefix("```").removesuffix("```").strip()
    if block_type == "quote":
        return string_to_strip.removeprefix(">").strip()
    if block_type == "ordered_list":
        start_index = (string_to_strip.find(". "))+2
        return string_to_strip[start_index:].strip()
    if block_type == "unordered_list":
        return string_to_strip[2:].strip()


def get_heading_count(text:str)-> int:
    """return heading cound based on num of # prefix."""
    if text.startswith("# "): return 1
    if text.startswith("## "): return 2
    if text.startswith("### "): return 3
    if text.startswith("#### "): return 4
    if text.startswith("##### "): return 5
    if text.startswith("###### "): return 6


def populate_html_node_for_list_blocks(list_type:str, block:str):
    """Convert each line in a block for a given list type."""
    tag = ""
    if list_type == "ordered_list":
        tag = "ol"
    else:
        tag ="ul"

    list_nodes = []
    for line in block.split("\n"):
        line_nodes = text_to_textnodes(strip_markdown_syntax(line, list_type))
        line_children = list(map(lambda x: text_node_to_html_node(x), line_nodes))
        list_nodes.append(ParentNode("li", line_children))
    return ParentNode(tag, list_nodes)


def populate_html_node_for_block(block_type:str, block:str) -> ParentNode:
    """Convert block to Parent and LeafNodes."""
    if block_type == "quote":
        new_lines = []
        for line in block.split("\n"):
            new_lines.append(strip_markdown_syntax(line, block_type))
        cleaned_block = "\n".join(new_lines)
        node_list = text_to_textnodes(cleaned_block)
        child_nodes =list(map(lambda x: text_node_to_html_node(x), node_list))
        return ParentNode(f"blockquote", child_nodes)
    if block_type not in ("ordered_list", "unordered_list"):
        node_list = text_to_textnodes(strip_markdown_syntax(block, block_type))
        child_nodes =list(map(lambda x: text_node_to_html_node(x), node_list))
        if block_type == "paragraph":
            return ParentNode("p", child_nodes)
        if block_type == "heading":
            return ParentNode(f"h{get_heading_count(block)}", child_nodes)
        if block_type == "code":
            code_node = ParentNode("code", child_nodes)
            return ParentNode("pre", [code_node])

    return populate_html_node_for_list_blocks(block_type, block)


def markdown_to_html(markdown:str)-> ParentNode:
    """Take markdown and convert to HTML Nodes"""
    blocks = markdown_to_blocks(markdown)
    block_html_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        block_html_nodes.append(populate_html_node_for_block(block_type, block))
    return ParentNode("div", block_html_nodes)


def markdown_to_blocks(markdown:str) -> list[str]:
    """split a body of markdown into list of blocks."""
    #blocks = markdown.splitlines(keepends=True)
    blocks = markdown.split("\n\n")
    blocks = list(map(lambda x: x.strip(), blocks))
    blocks = list(filter(lambda x: x!="", blocks))
    return blocks


def block_to_block_type(block_str:str) -> str:
    """return the type based on block string."""
    if block_str.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return "heading"
    if block_str.startswith("```") and block_str.endswith("```"):
        return "code"
    if block_str.startswith(">"):
        return "quote"
    if block_str.startswith(". ", 1) and block_str[0].isnumeric():
        return "ordered_list"
    if block_str.startswith(("- ", "* ")):
        return "unordered_list"
    return "paragraph"    


def text_to_textnodes(text: str) -> list[TextNode]:
    """Split markdown text into TextNodes."""
    node_list = [
        TextNode(text, text_type_text[0])
    ]
    node_list = split_nodes_delimiter(node_list, text_type_bold[1], text_type_bold[0])
    node_list = split_nodes_delimiter(node_list, text_type_italic[1], text_type_italic[0])
    node_list = split_nodes_delimiter(node_list, text_type_code[1], text_type_code[0])
    node_list = split_nodes_image(node_list)
    node_list = split_nodes_link(node_list)

    return node_list


def validate_delimiter_for_type(delimiter: str, text_type:str):
    if text_type == text_type_text[0] and delimiter == text_type_text[1]:
        return True
    if text_type == text_type_bold[0] and delimiter == text_type_bold[1]:
        return True
    if text_type == text_type_italic[0] and delimiter == text_type_italic[1]:
        return True
    if text_type == text_type_code[0] and delimiter == text_type_code[1]:
        return True
    if text_type == text_type_link[0] and delimiter == text_type_link[1]:
        return True
    if text_type == text_type_image[0] and delimiter == text_type_image[1]:
        return True
    raise ValueError("Invalid delimiter for given text type.")


def set_closing_delimiter(text_type:str)-> str:
    """Return closing delimiter for a given markdown type."""
    if text_type == text_type_text[0]:
        return text_type_text[1]
    if text_type == text_type_bold[0]:
        return text_type_bold[1]
    if text_type == text_type_italic[0]:
        return text_type_italic[1]
    if text_type == text_type_code[0]:
        return text_type_code[1]
    if text_type == text_type_link[0]:
        return text_type_link[2]
    if text_type == text_type_image[0]:
        return text_type_image[2]
    raise ValueError("Invalid text type.")


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter:str, text_type:str) -> list[TextNode]:
    """Split nodes by delimiter."""
    new_list = []
    if len(old_nodes)==0:
        return new_list
    
    validate_delimiter_for_type(delimiter, text_type)

    for node in old_nodes:
        if node.text_type == text_type_text[0] and delimiter in node.text:
            # split once on delimiter
            split_text = node.text.split(delimiter, maxsplit=1)

            if text_type == text_type_italic[0] and split_text[1][0] == delimiter:
                # split was on bold, need to discard split and see if * (singular) is anywhere else
                bold_split = node.text.split(delimiter*2)
                split_text = []
                split_text.append(f"{bold_split[0]}{delimiter*2}{bold_split[1]}{delimiter*2}")
                split_text.extend(bold_split[2:])
                if not delimiter in split_text[1]:
                    # no italic in node
                    new_list.append(node)
                    continue
                next_split = split_text[1].split(delimiter, maxsplit=1)
                split_text[0] += next_split[0]
                split_text[1] = next_split[1]
                

            closing_delimiter = set_closing_delimiter(text_type)
            if not closing_delimiter in split_text[1]:
                raise Exception("Closing Syntax not found. Invalid Markdown")
            new_list.append(TextNode(split_text[0], text_type_text[0]))
            next_split = split_text[1].split(closing_delimiter, maxsplit=1)
            new_list.append(TextNode(next_split[0], text_type))
            remaining_text=TextNode(next_split[1], text_type_text[0])
            # recursively call for rest of text.
            new_list.extend(split_nodes_delimiter([remaining_text], delimiter, text_type))
        else:
            new_list.append(node)
    
    return new_list

                
def extract_markdown_images(text:str) -> list[tuple]:
    """Extract image data from markdown."""
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)


def extract_markdown_links(text:str) -> list[tuple]:
    """Extract link data from markdown."""
    return re.findall(r"(?<!!)\[(.*?)\]\((.*?)\)", text)


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    """Split nodes for links."""
    new_list = []
    if len(old_nodes)==0:
        return new_list
    for node in old_nodes:
        if node.text_type == text_type_text[0] and text_type_link[1] in node.text:
            extracted_links = extract_markdown_links(node.text)
            if len(extracted_links) == 0:
                # no links, continue
                new_list.append(node)
                continue
            #else need to split text around each link
            sections = node.text.split(f"[{extracted_links[0][0]}]({extracted_links[0][1]})")
            new_list.append(TextNode(sections[0], text_type_text[0]))
            new_list.append(TextNode(extracted_links[0][0], text_type_link[0], extracted_links[0][1]))
            if len(sections[1]) > 0:
                remaining_text=TextNode(sections[1], text_type_text[0])
                # recursively call for rest of text.
                new_list.extend(split_nodes_link([remaining_text]))
        else:
            new_list.append(node)
    return new_list


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    """Split nodes for images."""
    new_list = []
    if len(old_nodes)==0:
        return new_list
    for node in old_nodes:
        if node.text_type == text_type_text[0] and text_type_image[1] in node.text:
            extracted_images = extract_markdown_images(node.text)
            if len(extracted_images) == 0:
                # no images, continue
                new_list.append(node)
                continue
            # else need to split text around each link
            sections = node.text.split(f"![{extracted_images[0][0]}]({extracted_images[0][1]})")
            new_list.append(TextNode(sections[0], text_type_text[0]))
            new_list.append(TextNode(extracted_images[0][0], text_type_image[0], extracted_images[0][1]))
            if len(sections[1])> 0:
                # recursively call for rest of text.
                remaining_text=TextNode(sections[1], text_type_text[0])
                new_list.extend(split_nodes_image([remaining_text]))
        else:
            new_list.append(node)
    return new_list
    
if __name__ == "__main__":
    main()