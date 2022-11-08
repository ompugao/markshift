# -*- coding: utf-8 -*-
import weakref

class Element(object):
    def __init__(self, parent = None, content = '', renderer = None):
        self.parent = parent  # must be None or weak reference
        self.content = content
        self.child_elements = []
        self.child_lines = []
        if renderer is None:
            raise ValueError('renderer must not be None')
        self.renderer = renderer

    def render(self,):
        return self.renderer.render(self)

class RawElement(Element):
    def __init__(self, parent, content, renderer):
        super().__init__(parent, content, renderer)

    def render(self,):
        return self.renderer.render_raw(self)

class StrongElement(Element):
    def __init__(self, parent, content, renderer):
        super().__init__(parent, content, renderer)

    def render(self,):
        return self.renderer.render_strong(self)


class ItalicElement(Element):
    def __init__(self, parent, content, renderer):
        super().__init__(parent, content, renderer)

    def render(self,):
        return self.renderer.render_italic(self)
