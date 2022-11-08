# -*- coding: utf-8 -*-

from .element import *
from enum import Enum
import re
import uuid

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
        self.regex_strong = re.compile('\[\* (.*)\]')
        self.regex_italic = re.compile('\[\/ (.*)\]')
        self.regex_command = re.compile('\[@ (.*)\]')
        self.regex_math = re.compile('\[\$ (.*?)\]')

        self.regex_quote = re.compile('^\[@quote(.*)\]')
        self.regex_code = re.compile('^\[@code (.*)\]')
        self.regex_math_command = re.compile('^\[@math(.*)\]')
        self.regex_raw = re.compile('``(.*)``')

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

        line_elem = Element(parent=weakref.proxy(parent),
                            renderer=self.renderer)

        # print(depth, line)
        mquote = self.regex_quote.match(line[depth:])
        if mquote is not None:
            self.state = State(ParseState.QUOTE, depth + 1)
            quote_elem = QuoteElement(parent=weakref.proxy(line_elem),
                                      content='',
                                      renderer=self.renderer)
            line_elem.child_elements.append(quote_elem)
            parent.child_lines.append(line_elem)
            return

        mcode = self.regex_code.match(line[depth:])
        if mcode is not None:
            self.state = State(ParseState.CODE, depth + 1)
            code_elem = CodeElement(parent=weakref.proxy(line_elem),
                                      content=mcode.group(1),
                                      renderer=self.renderer)
            line_elem.child_elements.append(code_elem)
            parent.child_lines.append(line_elem)
            return

        mmath = self.regex_math_command.match(line[depth:])
        if mmath is not None:
            self.state = State(ParseState.MATH, depth + 1)
            math_elem = MathElement(parent=weakref.proxy(line_elem),
                                    content=mmath.group(1),
                                    renderer=self.renderer,
                                    uid=uuid.uuid4(),
                                    inline=False)
            line_elem.child_elements.append(math_elem)
            parent.child_lines.append(line_elem)
            return

        if self.state.parse_state == ParseState.QUOTE and self.state.indent == depth:
            quoteelem = parent.child_elements[-1]
            assert(type(quoteelem) == QuoteElement)
            quoteelem.child_lines.extend(self._parse_str(quoteelem, line[depth:]))
            return
        elif self.state.parse_state == ParseState.CODE and self.state.indent == depth:
            codeelem = parent.child_elements[-1]
            assert(type(codeelem) == CodeElement)
            codeelem.child_lines.append(Element(parent=weakref.proxy(codeelem),
                                                content=line[depth:],
                                                renderer=self.renderer))
            return
        elif self.state.parse_state == ParseState.MATH and self.state.indent == depth:
            mathelem = parent.child_elements[-1]
            assert(type(mathelem) == MathElement)
            mathelem.child_lines.append(Element(parent=weakref.proxy(mathelem),
                                                content=line[depth:],
                                                renderer=self.renderer))
            return
        elif (self.state.parse_state != ParseState.LINE and self.state.indent != depth)\
            or self.state.parse_state == ParseState.LINE:
            self.state = State(ParseState.LINE, depth)
            line_elem.child_elements.extend(
                    self._parse_str(line_elem, line[depth:]))
            parent.child_lines.append(line_elem)
            return


    def _find_parent_line(self, parent, depth):
        if depth == 0:
            return parent
        if len(parent.child_lines) == 0:
            raise ValueError(f'Invalid indent')
        return self._find_parent_line(parent.child_lines[-1], depth - 1)

    def _parse_str(self, parent, s):
        elms = []
        # TODO
        # self.regex_raw.match(s)
        m = self.regex_strong.search(s)
        if m is not None:
            elms.extend(self._parse_str(parent, s[:m.start()]))

            el = StrongElement(parent=weakref.proxy(parent),
                               content='',
                               renderer=self.renderer)
            el.child_elements.extend(self._parse_str(el, m.group(1)))
            elms.append(el)

            elms.extend(self._parse_str(parent, s[m.end():]))
            return elms

        m = self.regex_italic.search(s)
        if m is not None:
            elms.extend(self._parse_str(parent, s[:m.start()]))

            el = ItalicElement(parent=weakref.proxy(parent),
                               content='',
                               renderer=self.renderer)
            el.child_elements.extend(self._parse_str(el, m.group(1)))
            elms.append(el)

            elms.extend(self._parse_str(parent, s[m.end():]))
            return elms


        m = self.regex_math.search(s)
        if m is not None:
            elms.extend(self._parse_str(parent, s[:m.start()]))

            el = MathElement(parent=weakref.proxy(parent),
                             content=m.group(1),
                             renderer=self.renderer,
                             uid=uuid.uuid4(),
                             inline=True)
            # el.child_elements.extend(self._parse_str(el, m.group(1)))
            elms.append(el)
            elms.extend(self._parse_str(parent, s[m.end():]))
            return elms


        return [Element(parent=weakref.proxy(parent),
                       content=s,
                       renderer=self.renderer)]
