# -*- coding: utf-8 -*-
from .htmlrenderer import HtmlRenderer
from io import StringIO
import html
import urllib.parse
import logging
import pathlib
from pygls.uris import from_fs_path

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

class HtmlRenderer4Preview(HtmlRenderer):

    def render_wikilink(self, elem):
        io = StringIO()
        io.write(f'<a href=\'javascript:on_wikilink_click("{elem.link}\");\'>{elem.link}</a>')
        return io.getvalue()

    def render_link(self, elem):
        log.debug(elem.link)
        videoid = get_youtube_id(elem.link)
        if videoid is not None:
            return f'<iframe class="videoContainer__video" width="640" height="480" src="http://www.youtube.com/embed/{videoid}?modestbranding=1&autoplay=0&controls=1&fs=0&loop=0&rel=0&showinfo=0&disablekb=1" frameborder="0"></iframe>'
             
        return super().render_link(elem)

    def render_img(self, elem):
        if '://' in elem.src:
            return super().render_img(elem)
            
        # assume a local file
        uripath = from_fs_path(str(pathlib.Path(elem.src).resolve()))
        io = StringIO()
        io.write(f'<img class="image" src="{uripath}" alt="{elem.alt} "')
        for key, value in elem.options.items():
            io.write(f'{key}={value}')
        io.write('/>')
        return io.getvalue()
