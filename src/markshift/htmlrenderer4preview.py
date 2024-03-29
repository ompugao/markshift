# -*- coding: utf-8 -*-
from .htmlrenderer import HtmlRenderer
from io import StringIO
import html
import urllib.parse
import logging
import pathlib
from pygls.uris import from_fs_path
from .element import *

import requests
import functools

log = logging.getLogger(__name__)

def get_youtube_id(value):
    """
    see: https://stackoverflow.com/questions/4356538/how-can-i-extract-video-id-from-youtubes-link-in-python

    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urllib.parse.urlparse(value)
    if query.netloc == 'youtu.be':
        return query.path[1:]
    if query.netloc in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urllib.parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None

@functools.lru_cache
def get_twitter_embed(tweet_url: str):
    """
    see https://medium.com/@avra42/how-to-embed-tweets-on-streamlit-web-application-247c01fdf767
    """

    query = urllib.parse.urlparse(tweet_url)
    if query.netloc != 'twitter.com':
        return None

    api = "https://publish.twitter.com/oembed?url={}".format(tweet_url)
    res = requests.get(api)
    try:
        j = res.json()
    except requests.exceptions.JSONDecodeError as e:
        return None
    if 'html' in j.keys():
        return j['html']
    else:
        return None

class HtmlRenderer4Preview(HtmlRenderer):

    def render(self, elem):
        io = StringIO()
        for el in elem.child_elements:
            io.write(el.render())
        if len(elem.child_lines) > 0:
            for line in elem.child_lines:
                io.write(line.render())
                if (type(line.child_elements[0]) not in [MathElement, \
                        QuoteElement, CodeElement, TableElement])\
                        and len(line.child_lines) == 0:
                    io.write('<br/>')
        tmp = io.getvalue()
        return tmp

    def render_wikilink(self, elem):
        io = StringIO()
        io.write(f'<a href=\'javascript:pywebview.api.on_wikilink_click("{elem.link}\");\'>{elem.link}</a>')
        return io.getvalue()

    def render_link(self, elem):
        if elem.link.is_local:
            link = from_fs_path(str(pathlib.Path(elem.link.path).resolve()))
        else:
            link = elem.link.path

        videoid = get_youtube_id(link)
        if videoid is not None:
            return f'<iframe class="videoContainer__video" width="640" height="480" src="http://www.youtube.com/embed/{videoid}?modestbranding=1&autoplay=0&controls=1&fs=1&loop=0&rel=0&showinfo=0&disablekb=0" frameborder="0"></iframe>'
             
        tweetembedding = get_twitter_embed(link)
        if tweetembedding is not None:
            return tweetembedding

        io = StringIO()
        io.write(f'<a href="{link}">{elem.content}</a>')
        return io.getvalue()

    def render_img(self, elem):
        if not elem.src.is_local:
            return super().render_img(elem)
            
        # resolve local path
        uripath = from_fs_path(str(pathlib.Path(elem.src.path).resolve()))
        io = StringIO()
        io.write(f'<img class="image" src="{uripath}" alt="{elem.alt} "')
        for key, value in elem.options.items():
            io.write(f'{key}={value}')
        io.write('/>')
        return io.getvalue()

    def render_text(self, elem):
        return f'{html.escape(elem.content)}'

    def render_code(self, elem):
        io = StringIO()
        if elem.inline:
            io.write('<code class="code-inline">')
            io.write(html.escape(elem.content))
            io.write('</code>')
        else:
            io.write('<pre><code class="language-')
            io.write(elem.lang)
            io.write('">')
            for line in elem.child_lines:
                io.write(line.render())
                io.write('\n')
            io.write('</code></pre>')
        return io.getvalue()

    def render_math(self, elem):
        io = StringIO()
        if elem.inline == True:
            io.write('<span class="math math-inline"><span class="katex">')
            io.write(elem.content)
            io.write('</span></span>')
        else:
            io.write('<div class="math math-display"><span class="katex-display">')
            for line in elem.child_lines:
                io.write(line.render())
                io.write('\n')
            io.write('</span></div>')
        return io.getvalue()

