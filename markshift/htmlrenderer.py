# -*- coding: utf-8 -*-
from .renderer import Renderer
from io import StringIO
import html

class HtmlRenderer(Renderer):
    def __init__(self, ):
        pass

    def render(self, elem):
        io = StringIO()
        io.write(elem.content)
        for el in elem.child_elements:
            io.write(el.render())
        if len(elem.child_lines) > 0:
            # io.write('<div class=tab>')
            io.write('<ul>')
            for line in elem.child_lines:
                # io.write(line.render() + '<br/>')
                io.write('<li>' + line.render() + '</li>')
            # io.write('</div>')
            io.write('</ul>')
        tmp = io.getvalue()
        # print('render: '+ tmp)
        return tmp

    def render_strong(self, elem):
        io = StringIO()
        io.write('<strong>')
        io.write(elem.content)
        for el in elem.child_elements:
            io.write(self.render(el))
        io.write('</strong>')
        return io.getvalue()

    def render_italic(self, elem):
        io = StringIO()
        io.write('<i>')
        io.write(elem.content)
        for el in elem.child_elements:
            io.write(self.render(el))
        io.write('</i>')
        return io.getvalue()

    def render_raw(self, elem):
        # TODO html escape
        return html.escape(elem.content)
