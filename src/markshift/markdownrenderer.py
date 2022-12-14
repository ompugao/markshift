# -*- coding: utf-8 -*-
from .renderer import Renderer
from io import StringIO
import html

class MarkdownRenderer(Renderer):
    def __init__(self, tabstep=4):
        self.indent = -1 
        self.tabstep = tabstep

    def render(self, elem):
        io = StringIO()
        for el in elem.child_elements:
            io.write(el.render())
        self.indent += 1
        for line in elem.child_lines:
            l = line.render() 
            io.write(l)
        self.indent -= 1
        tmp = io.getvalue()
        return tmp

    def render_line(self, elem):
        io = StringIO()
        offset = (' ' * self.tabstep * self.indent)
        io.write(offset + '- ')
        for el in elem.child_elements:
            io.write(el.render())
        io.write('\n')
        self.indent += 1
        for line in elem.child_lines:
            l = line.render() 
            io.write(l)
        self.indent -= 1
        return io.getvalue()

    def render_link(self, elem):
        io = StringIO()
        io.write(f'[{elem.content}]({elem.link.path})')
        return io.getvalue()

    def render_wikilink(self, elem):
        io = StringIO()
        io.write(f'[[{elem.link}]]')
        return io.getvalue()

    def render_text(self, elem):
        return elem.content

    def render_strong(self, elem):
        io = StringIO()
        io.write('**')
        for el in elem.child_elements:
            io.write(el.render())
        io.write('**')
        return io.getvalue()

    def render_italic(self, elem):
        io = StringIO()
        io.write('*')
        for el in elem.child_elements:
            io.write(el.render())
        io.write('*')
        return io.getvalue()

    def render_underline(self, elem):
        io = StringIO()
        io.write('<u>')
        for el in elem.child_elements:
            io.write(el.render())
        io.write('</u>')
        return io.getvalue()

    def render_deleted(self, elem):
        io = StringIO()
        io.write('<del>')
        for el in elem.child_elements:
            io.write(el.render())
        io.write('</del>')
        return io.getvalue()

    def render_heading(self, elem):
        io = StringIO()
        io.write('#' * elem.level)
        io.write(' ')
        io.write(elem.content)
        return io.getvalue()

    def render_math(self, elem):
        io = StringIO()
        if elem.inline == True:
            io.write('$ ')
            io.write(elem.content)
            io.write(' $')
            # io.write('</div>')
        else:
            io.write('\\[ \n')
            offset = (' ' * (self.tabstep * self.indent + len('- ')))
            for line in elem.child_lines:
                io.write(offset)
                io.write(line.render())
                io.write('\n')
            io.write(offset + '\\]')
        return io.getvalue()

    def render_quote(self, elem):
        io = StringIO()
        for iline, line in enumerate(elem.child_lines):
            offset = ''
            if iline > 0:
                offset = (' ' * (self.tabstep * self.indent + len('- ')))
            io.write(offset + '> ' + line.render() + '\n')
        return io.getvalue()

    def render_code(self, elem):
        io = StringIO()
        if elem.inline:
            io.write('`` ')
            io.write(elem.content)
            io.write(' ``')
        else:
            io.write(f'```{elem.lang}\n')
            offset = (' ' * (self.tabstep * self.indent + len('- ')))
            for line in elem.child_lines:
                io.write(offset)
                io.write(line.render())
                io.write('\n')
            io.write(offset)
            io.write('```')
        return io.getvalue()

    def render_table(self, elem):
        io = StringIO()
        offset = (' ' * (self.tabstep * self.indent + len('- ')))
        for irow, row in enumerate(elem.rows):
            if irow == 0:
                io.write((' ' * (self.tabstep * self.indent)))
            else:
                io.write(offset)
            
            if irow == 1:
                io.write('|')
                for _ in range(len(row)):
                    io.write(' ---- |')
                io.write('\n')
                io.write(offset)

            io.write('|')
            for i, e in enumerate(row):
                io.write(' ')
                io.write(e.render())
                io.write(' |')
            io.write('\n')
        return io.getvalue()


    def render_img(self, elem):
        io = StringIO()
        io.write(f'![{elem.alt}]({elem.src.path})')
        return io.getvalue()

