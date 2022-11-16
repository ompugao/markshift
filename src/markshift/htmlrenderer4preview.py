# -*- coding: utf-8 -*-
from .htmlrenderer import HtmlRenderer
from io import StringIO
import html

class HtmlRenderer4Preview(HtmlRenderer):

    def render_wikilink(self, elem):
        io = StringIO()
        io.write(f'<a href=\'javascript:on_wikilink_click("{elem.link}\");\'>{elem.link}</a>')
        return io.getvalue()

