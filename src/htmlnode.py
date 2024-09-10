"""HTML Node class"""

class HTMLNode():

    def __init__(self, tag:str|None=None, value:str|None=None, children:list|None=None, props:dict|None=None) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        prop_str = ""
        if isinstance(self.props, dict):
            for key in self.props:
                prop_str+=f'{key}="{self.props[key]}" '
            if prop_str != "":
                prop_str = prop_str[:-1]
        return prop_str
    
    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"


class LeafNode(HTMLNode):
    """Leaf Nodes."""
    def __init__(self, tag: str|None, value: str, props: dict | None = None) -> None:
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.value is None:
            raise ValueError("Value has not been set.")
        if self.tag is None:
            return self.value
        if self.props_to_html() != "":
            return f"<{self.tag} {self.props_to_html()}>{self.value}</{self.tag}>"
        return f"<{self.tag}>{self.value}</{self.tag}>"
    
    def __repr__(self) -> str:
        return f"LeafNode({self.tag}, {self.value}, {self.props})"
    
class ParentNode(HTMLNode):
    """Parent Nodes."""
    def __init__(self, tag: str, children: list, props: dict | None = None) -> None:
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("Tag has not been set.")
        if self.children is None or len(self.children)==0:
            raise ValueError("Expected Children.")
        
        child_html = list(map(lambda x: x.to_html(), self.children))
        if self.props_to_html() != "":
            return f"<{self.tag} {self.props_to_html()}>{''.join(child_html)}</{self.tag}>"
        return f"<{self.tag}>{''.join(child_html)}</{self.tag}>"

    def __repr__(self) -> str:
        return f"ParentNode({self.tag}, {self.children}, {self.props})"
    