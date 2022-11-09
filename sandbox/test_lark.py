from lark import Lark, Transformer, v_args
from lark import logger
import logging
logger.setLevel(logging.DEBUG)

try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass


grammar = """
    ?start: command
          | statement

    ?command: "[@" command_name (WS_INLINE+ parameter)* "]"
    ?command_name: "math" | "quote" | "code"
    ?parameter: WWORD
    ?statement: [expr|raw_sentence]*
    ?expr: expr_url_only
         | expr_url_title
         | expr_title_url
         | expr_builtin_symbols
         | expr_math
    ?expr_url_only: "[" URL "]"
    ?expr_url_title: "[" URL WS_INLINE+ WWORD "]"
    ?expr_title_url: "[" WWORD WS_INLINE+ URL "]"
    ?expr_builtin_symbols: "[" BUILTIN_NESTABLE_SYMBOLS+ WS_INLINE statement "]"
    ?expr_math: "[$" WS_INLINE latex_math_expr "$]"

    ?raw_sentence: NON_SQB_WORD+
    ?latex_math_expr: (WORD | NUMBER | WS_INLINE | MATH_SYMBOL)+

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

    NONSQB: /[^\[\]]/
    NON_SQB_WORD: NONSQB+
    URL: /\w+:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+/
    %import common.WS_INLINE
    %import common.NUMBER
"""


@v_args(inline=True)    # Affects the signatures of the methods
class CalculateTree(Transformer):
    from operator import add, sub, mul, truediv as div, neg
    number = float

    def __init__(self):
        self.vars = {}

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        try:
            return self.vars[name]
        except KeyError:
            raise Exception("Variable not found: %s" % name)


parser = Lark(grammar, parser='earley', keep_all_tokens=True, regex=True, g_regex_flags=1, debug=True) #, transformer=CalculateTree())

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
    print(parser.parse("こういう文章も[google https://google.com/]書けるんです"))
    print(parser.parse("URLの入れ子もできるかな?[*/ [google https://google.com/]] "))
    print(parser.parse("mathもできる？ [$ sum_{i=0}^{10} a_i $] "))
    print(parser.parse("できてそう [* [$ [O(n)] $]]"))


if __name__ == '__main__':
    test()
    # from IPython.terminal import embed; ipshell=embed.InteractiveShellEmbed(config=embed.load_default_config())(local_ns=locals())

    # # main()
