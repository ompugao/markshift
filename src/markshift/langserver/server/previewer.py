# -*- coding: utf-8 -*-
import configparser
import logging
import pathlib
import time
import webview
from pygls.lsp.types.window import ShowDocumentParams
from pygls.lsp.types import (Position, Range)
import platformdirs

# https://gist.github.com/walkermatt/2871026
from threading import Timer

def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                debounced.t.cancel()
            except(AttributeError):
                pass
            debounced.t = Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator

log = logging.getLogger(__name__)

class BasePreviewer(object):
    def __init__(self, ):
        pass

    def hide(self,):
        pass

    def show(self,):
        pass

    def set_title(self, title):
        pass

    def load_html(self, html):
        pass

    def destroy(self,):
        pass

    def start(self, fn, args):
        fn(args)

class PywebviewApi(object):
    def __init__(self, server):
        self.server = server

    def on_wikilink_click(self, pagename):
        pagename = pagename.removesuffix('.ms') + ".ms"  # ensure suffix
        params = ShowDocumentParams(
                uri = self.server.lsp.workspace.root_uri + '/' + pagename)
        # range = Range(start = Position(line = 3, character = 0),
        #               end = Position(line = 10, character = 0))
        # params.selection = range
        # log.info(params.uri)
        self.server.show_document(params)

class PywebviewPreviewer(BasePreviewer):

    def __init__(self, server, always_on_top=False, never_steal_focus=False, hidden_on_boot=False, zoom=1.0):
        self.server = server

        self.config = configparser.ConfigParser()
        self.configpath = str(pathlib.Path(platformdirs.user_data_dir('markshift', 'ompugao')) / 'previewer.ini')
        self.config.read(self.configpath)

        if not self.config.has_section('window'):
            self.config['window'] = {}
        x = int(self.config['window'].get('x', 0))
        y = int(self.config['window'].get('y', 0))
        w = int(self.config['window'].get('w', 600))
        h = int(self.config['window'].get('h', 400))

        self.window = webview.create_window('markshift_previewer',
                                            x=x, y=y, width=w, height=h,
                                            js_api=PywebviewApi(server),
                                            hidden=True,
                                            text_select=True,
                                            on_top=always_on_top)
        self.window.events.closing += self._on_closing
        self.window.events.resized += self._on_resized
        self.window.events.moved += self._on_moved

        self._never_steal_focus = never_steal_focus
        self._hidden_on_boot = hidden_on_boot
        self._zoom = zoom


    def start(self, fn, args):
        webview.start(self._start, (fn, args), gui='qt', debug=False)

    def _start(self, fn, args):
        time.sleep(1)
        view = self.window.gui.BrowserView.instances['master']

        if self._never_steal_focus:
            # do not steal focus
            from qtpy.QtCore import Qt
            view.setWindowFlag(Qt.WindowDoesNotAcceptFocus)
            time.sleep(0.1)

        view.view.setZoomFactor(self._zoom)

        if not self._hidden_on_boot:
            self.window.show()

        fn(args)

    def hide(self,):
        self.window.hide()

    def show(self,):
        self.window.show()

    def set_title(self, title):
        self.window.set_title(title)

    def load_html(self, html):
        self.window.load_html(html)

    def destroy(self,):
        self.window.destroy()
        self._save_geometry()

    def _on_resized(self, width, height):
        self.config['window']['w'] = str(width)
        self.config['window']['h'] = str(height)
        self._save_geometry()

    def _on_moved(self, x, y):
        self.config['window']['x'] = str(x)
        self.config['window']['y'] = str(y)
        self._save_geometry()

    def _on_closing(self,):
        self._save_geometry()

    @debounce(3)
    def _save_geometry(self,):
        pathlib.Path(self.configpath).parent.mkdir(parents=True, exist_ok=True)
        with open(self.configpath, 'w') as f:
            self.config.write(f)
