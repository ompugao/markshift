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

class ImageElement(Element):
    def __init__(self, parent, src, alt, renderer):
        super().__init__(parent, renderer)
        self.src = src
        self.alt = alt

    def render(self,):
        return self.renderer.render_img(self)
