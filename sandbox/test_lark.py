from lark import Lark, Transformer, v_args
from lark import logger
import logging
logger.setLevel(logging.DEBUG)

grammar = """
    ?start: expr_command
          | statement

    ?expr_command: "[@" command_name (WS_INLINE+ parameter)* "]"
    ?command_name: COMMAND
    ?parameter: WWORD -> parameter
    ?statement: [expr|raw_sentence]*
    ?expr: expr_url_only
         | expr_url_title
         | expr_title_url
         | expr_builtin_symbols
         | expr_math
         | expr_img
    ?expr_url_only: "[" url "]"
    ?expr_url_title: "[" url WS_INLINE+ url_title "]"
    ?expr_title_url: "[" url_title WS_INLINE+ url "]"
    ?url: URL -> url
    ?url_title: WWORD -> url_title
    ?expr_builtin_symbols: "[" symbols_applied  WS_INLINE statement "]"
    ?symbols_applied: BUILTIN_NESTABLE_SYMBOLS+ -> symbols
    ?expr_math: "[$" WS_INLINE latex_math_expr "$]"
    ?expr_img: "[@img" WS_INLINE img_path "]"
             | "[@img" WS_INLINE img_path WS_INLINE alt_img "]"
             | "[@img" WS_INLINE alt_img WS_INLINE img_path "]"
    ?img_path: URL | FILE_PATH -> img_path
    ?alt_img: ESCAPED_STRING -> alt_img

    ?raw_sentence: (NON_SQB_WORD|WS_INLINE)+
    ?latex_math_expr: (WORD | NUMBER | WS_INLINE | MATH_SYMBOL)+ -> latex_math_expr

    COMMAND: "math" | "quote" | "code"
    BUILTIN_NESTABLE_SYMBOLS: "*" | "/"
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
    URL: /\w+:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+/
    %import common.WS_INLINE
    %import common.ESCAPED_STRING
    %import common.NUMBER
"""


@v_args(inline=True)    # Affects the signatures of the methods
class HTMLTransformer(Transformer):
    def __init__(self):
        pass

    def expr_command(self, *parameters):
        print('expr_command')
        from IPython.terminal import embed; ipshell=embed.InteractiveShellEmbed(config=embed.load_default_config())(local_ns=locals())

    def expr_url_title(self, *params):
        from IPython.terminal import embed; ipshell=embed.InteractiveShellEmbed(config=embed.load_default_config())(local_ns=locals())

    def expr_title_url(self, title, _, url):
        from IPython.terminal import embed; ipshell=embed.InteractiveShellEmbed(config=embed.load_default_config())(local_ns=locals())

    def url(self, url):
        return url.value

    def url_title(self, url_title):
        return url_title.value

    def var(self, name):
        try:
            return self.vars[name]
        except KeyError:
            raise Exception("Variable not found: %s" % name)


parser = Lark(grammar, parser='earley', keep_all_tokens=False, regex=True, g_regex_flags=1, debug=True) #, transformer=CalculateTree())

    #'lalr' 'earley' 'cyk'
def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(parser.parse(s))


def test():
    print("---test---")
    print(parser.parse("[@quote]"))
    print(parser.parse("[@math]"))
    print(parser.parse("[@code python]"))
    print(parser.parse("[@math]"))
    print(parser.parse("[* bold text]"))
    print(parser.parse("[/ italic text]"))
    print(parser.parse("[/* bold italic text]"))
    print(parser.parse("[/ [* nested bold italic text]]"))
    print(parser.parse("[/ [* 日本語もOK text]]"))
    print(parser.parse("[/ [https://google.com google]]"))
    print(parser.parse(" [google https://google.com/]"))
    print(parser.parse("こういう文章も[google https://google.com/?query=1]書けるんです"))
    print(parser.parse("URLの入れ子もできるかな?[*/ [google https://google.com/]] "))
    print(parser.parse("mathもできる？ [$ sum_{i=0}^{10} a_i $] "))
    print(parser.parse("できてそう [* [$ [O(n)] $]]"))
    print(parser.parse("画像は？ [@img ../Pictures/Screenshot from 2021-09-13 16-47-23.png \"altテキストもいけるかな?\"]"))
    print(parser.parse("画像は？ どうじゃろ [@img \"前置altテキストもいけるかな?\" ../Pictures/Screenshot from 2021-09-13 16-47-23.png]"))


if __name__ == '__main__':
    test()
    from IPython.terminal import embed; ipshell=embed.InteractiveShellEmbed(config=embed.load_default_config())(local_ns=locals())

    # # main()
