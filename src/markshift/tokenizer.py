# -*- coding: utf-8 -*-
from lark import Lark, Transformer, v_args
from lark import logger
import lark
import uuid
import logging
logger.setLevel(logging.DEBUG)
from .exception import ParserError

grammar = """
    ?start: expr_command
          | statement

    ?expr_command: "[@" command_name (space_sep parameter)* "]" -> expr_command
    ?space_sep: WS_INLINE+ -> space_sep
    ?command_name: COMMAND
    ?parameter: WWORD -> parameter

    ?statement: [expr|raw_sentence]*

    ?expr: expr_img
         | expr_builtin_symbols
         | expr_code_inline
         | expr_math
         | expr_title_url
         | expr_url_title
         | expr_url_only
         | expr_wiki_link
    // wiki link must be the last

    ?expr_url_title: "[" url space_sep url_title "]"
    ?expr_title_url: "[" url_title space_sep url "]"
    ?expr_url_only: "[" url "]" -> expr_url_only
    ?url: URL
    // ?url_title: WWORD -> url_title
    // ?url_title: [WLETTER|" "]+ -> url_title
    ?url_title: [NONSQB|" "]+ -> url_title

    ?expr_wiki_link: "[" wiki_link "]" -> expr_wiki_link
    ?wiki_link: WIKILINKCHARS

    ?expr_builtin_symbols: "[" symbols_applied space_sep statement "]"
    ?symbols_applied: BUILTIN_NESTABLE_SYMBOLS+ -> symbols
    ?expr_code_inline: "[`" space_sep code_inline "`]" -> expr_code_inline
    ?expr_math: "[$" space_sep latex_math_expr "$]"
    ?expr_img: "[@img" space_sep img_path (space_sep img_option)* "]" -> expr_img_path_only
             | "[@img" space_sep img_path space_sep alt_img (space_sep img_option)* "]" -> expr_img_path_alt
             | "[@img" space_sep alt_img space_sep img_path (space_sep img_option)* "]" -> expr_alt_img_path
    ?img_path: URL | FILE_PATH
    ?alt_img: ESCAPED_STRING
    ?img_option: /[\w\d]+/ "=" /[\w\d]+/ -> img_option

    ?raw_sentence: (NON_SQB_WORD|WS_INLINE)+ -> raw_sentence
    ?code_inline: /.+?(?=`\])/ -> code_inline
    ?latex_math_expr: /.+?(?=\$\])/ -> latex_math_expr
    // match other than "$]"

    COMMAND: "math" | "quote" | "code" | /h[1-6]/ | "table"
    BUILTIN_NESTABLE_SYMBOLS: "*" | "/" | "_" | "-"
    LCASE_LETTER: "a".."z"
    UCASE_LETTER: "A".."Z"
    HIRAGANA_LETTER: /\p{Hiragana}/
    KATAKANA_LETTER: /\p{Katakana}/
    KANJI_LETTER: /\p{Han}/
    LETTER: UCASE_LETTER | LCASE_LETTER
    WORD: LETTER+
    WLETTER: UCASE_LETTER | LCASE_LETTER | HIRAGANA_LETTER | KATAKANA_LETTER | KANJI_LETTER
    WWORD: WLETTER+

    MATH_SYMBOL: /[^\p{L}\d\s]/u

    FILE_PATH: /([\/]?[\w_\-\s0-9\.]+)+\.([^\s\]]*)/u


    NONSQB: /[^\[\]]/
    NON_SQB_WORD: NONSQB+
    WIKILINKCHAR: /[^\[\]\/]/
    WIKILINKCHARS: WIKILINKCHAR+
    // URLTITLECHAR: /[^\[:\]\/]/
    // URLTITLECHARS: URLTITLECHAR+
    URL: /\w+:\/\/[\w\/:%#\$&\?\!\(\)~\.=\+\-]+/
    %import common.WS_INLINE
    %import common.ESCAPED_STRING
    %import common.NUMBER
"""

tokenizer = Lark(grammar, parser='earley', keep_all_tokens=False, regex=True, g_regex_flags=1, debug=False, propagate_positions=True)

from .element import *
@v_args(inline=True)    # Affects the signatures of the methods
class ElementTransformer(Transformer):
    def __init__(self, renderer):
        self.renderer = renderer

    def parameter(self, param):
        return param.value

    def space_sep(self, *args):
        return lark.visitors.Discard

    def expr_command(self, command, *params):
        command_name = command.value
        if command_name == 'quote':
            return QuoteElement(parent=None, renderer=self.renderer)
        elif command_name == 'code':
            if len(params) > 1:
                raise ParserError('too many parameters for code')
            if len(params) == 0:
                lang = ''
            else:
                lang = params[0]
            return CodeElement(parent=None, lang=lang, content='', inline=False, renderer=self.renderer)
        elif command_name == 'math':
            return MathElement(parent=None, content=' '.join(params), renderer=self.renderer, uid=uuid.uuid4(), inline=False)
        elif command_name in ['h' + str(i) for i in range(1, 7)]:
            level = int(command_name[1])
            return HeadingElement(parent=None, level=level, content=' '.join(params), renderer=self.renderer)
        elif command_name == 'table':
            return TableElement(parent=None, renderer=self.renderer)
        raise ParserError('Invalid command: %s'%command_name)

    def symbols(self, *tokens):
        return [t.value for t in tokens]

    def expr_builtin_symbols(self, symbols, *elements):
        def _strong(child_elems):
            elem = StrongElement(parent=None, renderer=self.renderer)
            elem.child_elements.extend(child_elems)
            return elem
        def _italic(child_elems):
            elem = ItalicElement(parent=None, renderer=self.renderer)
            elem.child_elements.extend(child_elems)
            return elem
        def _underline(child_elems):
            elem = UnderlineElement(parent=None, renderer=self.renderer)
            elem.child_elements.extend(child_elems)
            return elem
        def _deleted(child_elems):
            elem = DeletedElement(parent=None, renderer=self.renderer)
            elem.child_elements.extend(child_elems)
            return elem
        assert(len(symbols) > 0)
        child = list(elements)
        for s in symbols:
            if s == '*':
                child = [_strong(child)]
            elif s == '/':
                child = [_italic(child)]
            elif s == '_':
                child = [_underline(child)]
            elif s == '-':
                child = [_deleted(child)]
        return child[0]

    def expr_math(self, latex_math):
        return MathElement(parent=None, content=latex_math, renderer=self.renderer, uid=uuid.uuid4(), inline=True)

    def latex_math_expr(self, *tokens):
        mathexpr = ''.join([t.value for t in tokens])
        return mathexpr
        # return TextElement(parent=None, content=mathexpr, renderer=self.renderer)

    def raw_sentence(self, text):
        return TextElement(parent=None, content=text.value, renderer=self.renderer)

    def statement(self, *elements):
        compound = Element(parent=None, renderer=self.renderer)
        compound.child_elements.extend(elements)
        return compound

    def URL(self, url):
        return url.value

    def url_title(self, *args):
        return ''.join([a.value for a in args])

    def expr_code_inline(self, code):
        return CodeElement(parent=None, lang=None, content=code, inline=True, renderer=self.renderer)

    def code_inline(self, s):
        return s.value

    def expr_url_only(self, url):
        return LinkElement(parent=None, content=url, link=url, renderer=self.renderer)

    def expr_url_title(self, url, title):
        return LinkElement(parent=None, content=title, link=url, renderer=self.renderer)

    def expr_title_url(self, title, url):
        return LinkElement(parent=None, content=title, link=url, renderer=self.renderer)

    def expr_wiki_link(self, wiki_link):
        return WikiLinkElement(parent=None, content='', link=wiki_link.value, pos=[wiki_link.line, wiki_link.column, wiki_link.start_pos, wiki_link.end_pos], renderer=self.renderer)

    def FILE_PATH(self, path):
        return path.value

    def ESCAPED_STRING(self, s):
        return s[1:-1]

    def _validate_img_options(self, options):
        for key, value in options.items():
            if not key in ["width", "height"]:
                raise ParserError('Invalid image option: %s'%key)
            if key == 'width' or key == 'height':
                options[key] = int(value)
        return options


    def expr_img_path_only(self, path, *options):
        options = self._validate_img_options(dict(options))
        return ImageElement(parent=None, src=path, alt='', options=options, renderer=self.renderer)

    def expr_img_path_alt(self, path, alt, *options):
        options = self._validate_img_options(dict(options))
        return ImageElement(parent=None, src=path, alt=alt, options=options, renderer=self.renderer)

    def expr_alt_img_path(self, alt, path, *options):
        options = self._validate_img_options(dict(options))
        return ImageElement(parent=None, src=path, alt=alt, options=options, renderer=self.renderer)

    def img_option(self, key, value):
        return (key.value, value.value)

