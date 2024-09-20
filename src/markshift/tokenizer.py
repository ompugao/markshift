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

    // expr_command is not an inline command. this must not succeed or precede any string.
    ?expr_command: "[@" command_name (space_sep parameter)* "]" -> expr_command
    ?space_sep: WS_INLINE+ -> space_sep
    ?command_name: COMMAND
    ?parameter: WWORD -> parameter

    ?statement: [expr|raw_sentence]*

    ?expr: expr_img              // | expr_atag
         | expr_builtin_symbols
         | expr_code_inline
         | expr_math
         | expr_title_url
         | expr_url_title
         | expr_url_only
         | expr_local_file_title
         | expr_title_local_file
         | expr_local_file_only
         | expr_wiki_link
    // wiki link must be the last

    ?expr_url_title: "[" url space_sep url_title "]"
    ?expr_title_url: "[" url_title space_sep url "]"
    ?expr_url_only: "[" url "]" -> expr_url_only
    ?url: URL -> url
    ?url_title: [NONSQB|" "]+ -> url_title

    ?expr_local_file_title: "[" relative_local_file space_sep local_file_title "]"
    ?expr_title_local_file: "[" local_file_title space_sep relative_local_file "]"
    ?expr_local_file_only:  "[" relative_local_file "]" -> expr_local_file_only
    ?local_file_title: url_title
    ?relative_local_file: STRICT_FILE_PATH -> relative_local_file

    ?expr_wiki_link: "[" wiki_link "]" -> expr_wiki_link
    ?wiki_link: WIKILINKCHARS

    ?expr_builtin_symbols: "[" symbols_applied space_sep statement "]"
    ?symbols_applied: BUILTIN_NESTABLE_SYMBOLS+ -> symbols
    ?expr_code_inline: "[`" code_inline "`]" -> expr_code_inline
    ?expr_math: "[$" latex_math_expr "$]" -> expr_math
    ?expr_img: "[@img" space_sep img_path (space_sep img_option)* "]" -> expr_img_path_only
             | "[@img" space_sep img_path space_sep alt_img (space_sep img_option)* "]" -> expr_img_path_alt
             | "[@img" space_sep alt_img space_sep img_path (space_sep img_option)* "]" -> expr_alt_img_path
    ?img_path: url | local_file
    ?local_file: FILE_PATH -> local_file
    ?alt_img: ESCAPED_STRING
    ?img_option: /[\w\d]+/ "=" /[\w\d]+/ -> img_option

    // ?expr_atag: "[@a" space_sep atag_path "]" -> expr_atag_path_only
    //          | "[@a" space_sep atag_path space_sep alt_atag "]" -> expr_atag_path_alt
    //          | "[@a" space_sep alt_atag space_sep atag_path "]" -> expr_alt_atag_path
    // ?atag_path: url | local_file
    // ?alt_atag: ESCAPED_STRING

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

    FILE_PATH: /([\w_\-\s0-9\.]+\/)+([\w_\-\s0-9\.]+)\.([^\s\]]*)/u
    // this must be a relative path which starts from './' or '../'
    STRICT_FILE_PATH: /\.\.?\/([\w_\-\s0-9\.]+\/)*([\w_\-\s0-9\.]+)\.([^\s\]]+)/u 


    NONSQB: /[^\[\]]/
    NON_SQB_WORD: NONSQB+
    WIKILINKCHAR: /[^\[\]\/\.]/
    WIKILINKCHARS: WIKILINKCHAR+
    // URLTITLECHAR: /[^\[:\]\/]/
    // URLTITLECHARS: URLTITLECHAR+
    URL: /\w+:\/\/[\w\/:%#\$&\?\!\(\)~\.=\+\-\:@]+/
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
                raise ParserError('too many parameters for code', command.line, command.column)
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
        raise ParserError('Invalid command: %s'%command_name, command.line, command.column)

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

    def url(self, url):
        return Path(url, is_local=False)

    def URL(self, url):
        return url.value

    def local_file(self, path):
        return Path(path, True)

    def relative_local_file(self, path):
        return Path(path, True)

    def url_title(self, *args):
        if len(args) == 1 and args[0] == None:
            # must be only spaces, such as:
            # [https://google.com/     ]
            # we replace it with '-' to make it recognizable
            # return '-'
            raise ParserError("url title is empty", 0, 0)
        return ''.join([a.value for a in args])

    def expr_code_inline(self, code):
        return CodeElement(parent=None, lang=None, content=code, inline=True, renderer=self.renderer)

    def code_inline(self, s):
        return s.value

    def expr_url_only(self, url):
        return LinkElement(parent=None, content=url.path, link=url, renderer=self.renderer)

    def expr_url_title(self, url, title):
        return LinkElement(parent=None, content=title, link=url, renderer=self.renderer)

    def expr_title_url(self, title, url):
        return LinkElement(parent=None, content=title, link=url, renderer=self.renderer)

    def expr_local_file_only(self, local_file):
        return LinkElement(parent=None, content=local_file.path, link=local_file, renderer=self.renderer)

    def expr_local_file_title(self, local_file, title):
        return LinkElement(parent=None, content=title, link=local_file, renderer=self.renderer)

    def expr_title_local_file(self, title, local_file):
        return LinkElement(parent=None, content=title, link=local_file, renderer=self.renderer)

    def expr_wiki_link(self, wiki_link):
        return WikiLinkElement(parent=None, content='', link=wiki_link.value, pos=[wiki_link.line, wiki_link.column, wiki_link.start_pos, wiki_link.end_pos], renderer=self.renderer)

    def FILE_PATH(self, path):
        return path.value

    def ESCAPED_STRING(self, s):
        return s[1:-1]

    def _validate_img_options(self, options):
        for key, value in options.items():
            if not key.value in ["width", "height"]:
                raise ParserError('Invalid image option: %s'%key, key.line, key.column)
            if key.value == 'width' or key.value == 'height':
                options[key.value] = int(value.value)
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

    # def expr_atag_path_only(self, path, *options):
    #     # options = self._validate_atag_options(dict(options))
    #     return LinkElement(parent=None, content=path.path, link=path, renderer=self.renderer)

    # def expr_atag_path_alt(self, path, alt, *options):
    #     # options = self._validate_atag_options(dict(options))
    #     return LinkElement(parent=None, content=alt, link=path, renderer=self.renderer)

    # def expr_alt_atag_path(self, alt, path, *options):
    #     # options = self._validate_atag_options(dict(options))
    #     return LinkElement(parent=None, content=alt, link=path, renderer=self.renderer)

    def img_option(self, key, value):
        return (key, value)

