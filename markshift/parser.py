# -*- coding: utf-8 -*-

from .element import *
from enum import Enum
import re

class ParseState(Enum):
    LINE = 0
    CODE = 1
    MATH = 2
    # TABLE = 2

class Parser(object):
    def __init__(self, renderer):
        self.state = ParseState.LINE
        self.renderer = renderer
        self.regex_indent = re.compile('^(\t*)')
        self.regex_strong = re.compile('\[\* (.*)\]')
        self.regex_italic = re.compile('\[\/ (.*)\]')
        self.regex_raw = re.compile('``(.*)``')

    def parse(self, lines):
        root_element = Element(renderer=self.renderer)
        root_element = self._parse(root_element, root_element, lines)
        return root_element

    def _parse(self, root, parent, lines):
        for line in lines:
            line_elem, parent = self._parse_line(root, line)
            parent.child_lines.append(line_elem)
        return root


    def _parse_line(self, root, line):
        depth = self.regex_indent.match(line).end()
        parent = self._find_parent_line(root, depth)

        line_elem = Element(parent=weakref.proxy(parent),
                            renderer=self.renderer)
        line_elem.child_elements.append(
                self._parse_str(line_elem, line[depth:]))
        return line_elem, parent

    def _find_parent_line(self, parent, depth):
        if depth == 0:
            return parent
        if len(parent.child_lines) == 0:
            raise ValueError(f'Invalid indent')
        return self._find_parent_line(parent.child_lines[-1], depth - 1)

    def _parse_str(self, parent, s):
        self.regex_raw
        m = self.regex_strong.match(s)
        if m is not None:
            el = StrongElement(parent=weakref.proxy(parent),
                               content='',
                               renderer=self.renderer)
            el.child_elements.append(self._parse_str(el, m.group(1)))
            return el
        m = self.regex_italic.match(s)
        if m is not None:
            el = ItalicElement(parent=weakref.proxy(parent),
                               content='',
                               renderer=self.renderer)
            el.child_elements.append(self._parse_str(el, m.group(1)))
            return el
        return Element(parent=weakref.proxy(parent),
                       content=s,
                       renderer=self.renderer)
