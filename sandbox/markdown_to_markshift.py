"""
Markshift renderer for mistletoe.
"""

from itertools import chain
import mistletoe.latex_token as latex_token
from mistletoe.base_renderer import BaseRenderer
import string


# (customizable) delimiters for inline code
verb_delimiters = string.punctuation + string.digits
for delimiter in ']':  # remove invalid delimiters
    verb_delimiters.replace(delimiter, '')
for delimiter in reversed('|!"\'=+'):  # start with most common delimiters
    verb_delimiters = delimiter + verb_delimiters.replace(delimiter, '')


class MarkshiftRenderer(BaseRenderer):
    def __init__(self, *extras):
        """
        Args:
            extras (list): allows subclasses to add even more custom tokens.
        """
        tokens = self._tokens_from_module(latex_token)
        self.verb_delimiters = verb_delimiters
        super().__init__(*chain(tokens, extras))

    def render_strong(self, token):
        return '[* {}]'.format(self.render_inner(token))

    def render_emphasis(self, token):
        return '[/ {}]'.format(self.render_inner(token))

    def render_inline_code(self, token):
        content = self.render_raw_text(token.children[0], escape=False)

        # search for delimiter not present in content
        # for delimiter in self.verb_delimiters:
        #     if delimiter not in content:
        #         break

        # if delimiter in content:  # no delimiter found
        #     raise RuntimeError('Unable to find delimiter for verb macro')

        template = '[` {content} `]'
        return template.format(content=content)

    def render_strikethrough(self, token):
        return '[- {}]'.format(self.render_inner(token))

    def render_image(self, token):
        return '[@img {}]'.format(token.src)

    def render_link(self, token):
        template = '[{target} {inner}]'
        inner = self.render_inner(token)
        return template.format(target=token.target, inner=inner)

    def render_auto_link(self, token):
        return f'[{token.target}]'

    # @staticmethod
    def render_math(self, token):
        return '[@math]\n' + '\n'.join(['\t'+e for e in token.content.split('\n')])

    def render_escape_sequence(self, token):
        return self.render_inner(token)

    def render_raw_text(self, token, escape=True):
        return token.content
        # return (token.content.replace('$', '\\$').replace('#', '\\#')
        #                      .replace('{', '\\{').replace('}', '\\}')
        #                      .replace('&', '\\&').replace('_', '\\_')
        #                      .replace('%', '\\%')
        #        ) if escape else token.content

    def render_heading(self, token):
        inner = self.render_inner(token)
        return f'[@h{token.level} {inner}]'

    def render_quote(self, token):
        template = '[@quote]\n{inner}\n'
        inner = self.render_inner(token)
        newinner = []
        for line in inner.split('\n'):
            if line != '':
                newinner.append('\t' + line)
        return template.format(inner='\n'.join(newinner))

    def render_paragraph(self, token):
        return '\n{}\n'.format(self.render_inner(token))

    def render_block_code(self, token):
        inner = self.render_inner(token)
        newinner = []
        for line in inner.split('\n'):
            if line != '':
                newinner.append('\t' + line)
        newinner = '\n'.join(newinner)
        return (f'\n[@code {token.language}]\n{newinner}\n')

    def render_list(self, token):
        inner = self.render_inner(token)
        newinner = []
        for line in inner.split('\n'):
            if line != '':
                newinner.append('\t' + line)
        return '\n'.join(newinner)

    def render_list_item(self, token):
        return self.render_inner(token)

    def render_table(self, token):
        if hasattr(token, 'header'):
            head_template = '{inner}\n'
            head_inner = self.render_table_row(token.header)
            head_rendered = head_template.format(inner=head_inner)
        else:
            head_rendered = ''
        inner = self.render_inner(token)
        
        newinner = []
        for line in (head_rendered + inner).split('\n'):
            newinner.append('\t' + line)
        newinner = '\n'.join(newinner)
        return f'[@table]\n{newinner}\n'

    def render_table_row(self, token):
        cells = [self.render(child) for child in token.children]
        return '\t'.join(cells)

    def render_table_cell(self, token):
        return self.render_inner(token)

    @staticmethod
    def render_thematic_break(token):
        return '\n'

    @staticmethod
    def render_line_break(token):
        return '\n' if token.soft else '\n'

    def render_document(self, token):
        return self.render_inner(token)
