# -*- coding: utf-8 -*-
from .renderer import Renderer
from io import StringIO
import html

class HtmlRenderer(Renderer):
    def __init__(self, ):
        pass

    def render(self, elem):
        io = StringIO()
        for el in elem.child_elements:
            io.write(el.render())
        if len(elem.child_lines) > 0:
            # io.write('<ul>')
            # for line in elem.child_lines:
            #     l = line.render() 

            #     if l == '':
            #         io.write('<li class="empty-line">' + l + '<br/></li>')
            #     else:
            #         io.write('<li>' + l + '</li>')
            # io.write('</ul>')
            for line in elem.child_lines:
                io.write(line.render())
                if len(line.child_lines) == 0:
                    io.write('<br/>')
        tmp = io.getvalue()
        return tmp

    def render_line(self, elem):
        io = StringIO()
        for el in elem.child_elements:
            io.write(el.render())
        if len(elem.child_lines) > 0:
            io.write('<ul>')
            for line in elem.child_lines:
                l = line.render() 
                if l == '':
                    io.write('<li class="empty-line">' + l + '<br/></li>')
                else:
                    io.write('<li>' + l + '</li>')
            io.write('</ul>')
        return io.getvalue()

    def render_link(self, elem):
        io = StringIO()
        io.write(f'<a href="{elem.link.path}">{elem.content}</a>')
        return io.getvalue()

    def render_wikilink(self, elem):
        io = StringIO()
        io.write(f'<a href="{elem.link}">{elem.link}</a>')
        return io.getvalue()

    def render_text(self, elem):
        #TODO?
        return html.escape(elem.content)

    def render_strong(self, elem):
        io = StringIO()
        io.write('<b>')
        for el in elem.child_elements:
            io.write(el.render())
        io.write('</b>')
        return io.getvalue()

    def render_italic(self, elem):
        io = StringIO()
        io.write('<i>')
        for el in elem.child_elements:
            io.write(el.render())
        io.write('</i>')
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
        tag = 'h' + str(elem.level)
        io.write(f'<{tag}>')
        io.write(elem.content)
        io.write(f'</{tag}>')
        return io.getvalue()

    def render_math(self, elem):
        io = StringIO()
        if elem.inline == True:
            # io.write(f'<div id={elem.uid}/>')
            io.write('$$ ')
            io.write(elem.content)
            io.write(' $$')
            # io.write('</div>')
        else:
            io.write('[[ ')
            for line in elem.child_lines:
                io.write(line.render())
                io.write('\n')
            io.write(' ]]')
        return io.getvalue()

    def render_quote(self, elem):
        io = StringIO()
        io.write('<blockquote>')
        for line in elem.child_lines:
            io.write(line.render() + '<br/>')
        io.write('</blockquote>')
        return io.getvalue()

    def render_code(self, elem):
        io = StringIO()
        if elem.inline:
            io.write('<code>')
            io.write(html.escape(elem.content))
            io.write('</code>')
        else:
            io.write('<pre><code class="')
            io.write(elem.lang)
            io.write('">')
            for line in elem.child_lines:
                io.write(line.render())
                io.write('\n')
            io.write('</code></pre>')
        return io.getvalue()

    def render_table(self, elem):
        io = StringIO()
        io.write('<table>\n')
        for row in elem.rows:
            io.write('<tr>')
            for td in row:
                io.write('<td>')
                io.write(td.render())
                io.write('</td>')
            io.write('</tr>')
            io.write('\n')
        io.write('</table>\n')
        return io.getvalue()

    def render_img(self, elem):
        io = StringIO()
        io.write(f'<img class="image" src="{elem.src.path}" alt="{elem.alt} "')
        for key, value in elem.options.items():
            io.write(f'{key}={value}')
        io.write('/>')
        return io.getvalue()
