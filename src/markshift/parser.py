# -*- coding: utf-8 -*-

from .element import *
from .tokenizer import tokenizer, ElementTransformer
from .exception import ParserError
from enum import Enum
import re
import uuid
import lark.exceptions

class ParseState(Enum):
    LINE = 0
    QUOTE = 1
    CODE = 2
    MATH = 3
    # TABLE = 2

class State(object):
    def __init__(self, parse_state = ParseState.LINE, indent = 0):
        self.parse_state = parse_state
        self.indent = indent

class Parser(object):
    def __init__(self, renderer):
        self.state = State(ParseState.LINE, 0)

        self.renderer = renderer
        self.regex_indent = re.compile('^(\t*)')

        self.tokenizer = tokenizer
        self.transformer = ElementTransformer(renderer)

    def parse(self, lines):
        root_element = Element(renderer=self.renderer)
        root_element = self._parse(root_element, root_element, lines)
        return root_element

    def _parse(self, root, parent, lines):
        for line in lines:
            self._parse_line(root, line)
        return root


    def _parse_line(self, root, line):
        depth = self.regex_indent.match(line).end()
        if self.state.parse_state != ParseState.LINE and depth > self.state.indent:
            depth = self.state.indent
        parent = self._find_parent_line(root, depth)

        if self.state.parse_state != ParseState.LINE and self.state.indent == depth:
            if self.state.parse_state == ParseState.QUOTE:
                quoteelem = parent.child_elements[-1]
                assert(type(quoteelem) == QuoteElement)
                quoteelem.child_lines.append(self._parse_str(quoteelem, line[depth:]))
                return
            else:
                blockelem = parent.child_elements[-1]
                assert(type(blockelem) in [MathElement, CodeElement])
                blockelem.child_lines.append(TextElement(parent=weakref.proxy(blockelem),
                                                         content=line[depth:],
                                                         renderer=self.renderer))
                return

        line_elem = LineElement(parent=weakref.proxy(parent),
                                renderer=self.renderer)

        # print(depth, " ", line)
        parsed_elem = self._parse_str(parent, line[depth:])

        if type(parsed_elem) is QuoteElement:
            self.state = State(ParseState.QUOTE, depth + 1)
        elif type(parsed_elem) is CodeElement:
            self.state = State(ParseState.CODE, depth + 1)
        elif type(parsed_elem) is MathElement:
            self.state = State(ParseState.MATH, depth + 1)
        else:
            self.state = State(ParseState.LINE, depth)
        line_elem.child_elements.append(parsed_elem)
        parent.child_lines.append(line_elem)
        return

    def _find_parent_line(self, parent, depth):
        if depth == 0:
            return parent
        if len(parent.child_lines) == 0:
            raise ParserError(f'Invalid indent')
        return self._find_parent_line(parent.child_lines[-1], depth - 1)

    def _parse_str(self, parent, s):
        if len(s) == 0:
            return TextElement(weakref.proxy(parent), content='', renderer=self.renderer)
        try:
            tree = tokenizer.parse(s)
        except lark.exceptions.UnexpectedEOF as e:
            return TextElement(weakref.proxy(parent), content=s, renderer=self.renderer)
        return self.transformer.transform(tree)

