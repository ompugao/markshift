# -*- coding: utf-8 -*-
import weakref
from io import StringIO

class Element(object):
    def __init__(self, parent = None, renderer = None):
        self.parent = parent  # must be None or weak reference
        self.child_elements = []
        self.child_lines = []
        if renderer is None:
            raise ValueError('renderer must not be None')
        self.renderer = renderer

    def render(self,):
        """
        generic render
        """
        return self.renderer.render(self)

class LineElement(Element):
    def __init__(self, parent, renderer):
        super().__init__(parent, renderer)

    def render(self,):
        return self.renderer.render_line(self)

class LinkElement(Element):
    def __init__(self, parent, content, link, renderer):
        super().__init__(parent, renderer)
        self.content= content
        self.link = link

    def render(self,):
        return self.renderer.render_link(self)

class WikiLinkElement(LinkElement):
    def __init__(self, parent, content, link, pos, renderer):
        super().__init__(parent, content, link, renderer)
        self.line, self.column, self.end_line, self.end_column = pos

    def render(self,):
        return self.renderer.render_wikilink(self)

class TextElement(Element):
    def __init__(self, parent, content, renderer):
        self.content = content
        super().__init__(parent, renderer)

    def render(self,):
        return self.renderer.render_text(self)

class StrongElement(Element):
    def __init__(self, parent, renderer):
        super().__init__(parent, renderer)

    def render(self,):
        return self.renderer.render_strong(self)


class ItalicElement(Element):
    def __init__(self, parent, renderer):
        super().__init__(parent, renderer)

    def render(self,):
        return self.renderer.render_italic(self)

class UnderlineElement(Element):
    def __init__(self, parent, renderer):
        super().__init__(parent, renderer)

    def render(self,):
        return self.renderer.render_underline(self)

class DeletedElement(Element):
    def __init__(self, parent, renderer):
        super().__init__(parent, renderer)

    def render(self,):
        return self.renderer.render_deleted(self)

class HeadingElement(Element):
    """
    Heading (h1~h6) is not recommended to be used.
    This is just for compatibility with markdown/html.
    Instaed, just indent them, which will make texts portable.

    Note: I know that the opinion above is not suitable for those who are visually impaired.
    I hope browsers can help them to jump between the not-indented lines in a document easily.
    """
    def __init__(self, parent, level, content, renderer):
        super().__init__(parent, renderer)
        self.level = level
        self.content = content

    def render(self,):
        return self.renderer.render_heading(self)

class MathElement(Element):
    def __init__(self, parent, content, renderer, uid, inline=False):
        super().__init__(parent, renderer)
        self.uid = uid
        self.inline = inline
        self.content= content

    def render(self,):
        return self.renderer.render_math(self)

class QuoteElement(Element):
    def __init__(self, parent, renderer):
        super().__init__(parent, renderer)

    def render(self,):
        return self.renderer.render_quote(self)

class CodeElement(Element):
    def __init__(self, parent, lang, content, inline, renderer):
        super().__init__(parent, renderer)
        self.lang = lang
        self.content = content
        self.inline = inline

    def render(self,):
        return self.renderer.render_code(self)

class TableElement(Element):
    def __init__(self, parent, renderer):
        super().__init__(parent, renderer)
        self.rows = []

    def render(self,):
        return self.renderer.render_table(self)

class ImageElement(Element):
    def __init__(self, parent, src, alt, options, renderer):
        super().__init__(parent, renderer)
        self.src = src
        self.alt = alt
        self.options = options

    def render(self,):
        return self.renderer.render_img(self)
