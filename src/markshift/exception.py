# -*- coding: utf-8 -*-

class ParserError(Exception):
    line: int
    column: int
    def __init__(self, msg, line, column):
        super().__init__(msg)
        self.line = line
        self.column = column

