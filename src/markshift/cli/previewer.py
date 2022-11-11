#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(''))
import click
import re
import threading
import logging
import socketserver
from functools import partial

from pylsp_jsonrpc.dispatchers import MethodDispatcher
from pylsp_jsonrpc.endpoint import Endpoint
from pylsp_jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter


try:
    import ujson as json
except Exception:  # pylint: disable=broad-except
    import json
import webview

import markshift.parser
import markshift.htmlrenderer

log = logging.getLogger(__name__)


template = """
<!DOCTYPE html>
<head>
<!-- highlight.js -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.6.0/styles/github.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.6.0/highlight.min.js"></script>
<script>hljs.highlightAll();</script>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/github-markdown.min.css"/>

<!-- katex -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.3/dist/katex.min.css" integrity="sha384-Juol1FqnotbkyZUT5Z7gUPjQ9gzlwCENvUZTpQBAPxtusdwFLRy382PSDx5UUJ4/" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.3/dist/katex.min.js" integrity="sha384-97gW6UIJxnlKemYavrqDHSX3SiygeOwIZhwyOKRfSaf0JWKRVj9hLASHgFTzT+0O" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.3/dist/contrib/auto-render.min.js" integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05" crossorigin="anonymous"></script>
<script>
    document.addEventListener("DOMContentLoaded", function() {
        renderMathInElement(document.body, {
          // customised options
          // • auto-render specific keys, e.g.:
          delimiters: [
              {left: '$$', right: '$$', display: false},
              {left: '$', right: '$', display: false},
              {left: '\\[\\[', right: '\\]\\]', display: true}
          ],
          // • rendering keys, e.g.:
          throwOnError : false
        });
    });
</script>
<style>
.empty-line{
    list-style-type: none;
}
.image {
    vertical-align: top; 
}
</style>
</head>
<body>
<div id="body-content"/>
</body>
</html>
"""   

# LINT_DEBOUNCE_S = 0.5  # 500 ms
# PARENT_PROCESS_WATCH_INTERVAL = 10  # 10 s
MAX_WORKERS = 64
# PYTHON_FILE_EXTENSIONS = ('.py', '.pyi')
# CONFIG_FILEs = ('pycodestyle.cfg', 'setup.cfg', 'tox.ini', '.flake8')


class _StreamHandlerWrapper(socketserver.StreamRequestHandler):
    """A wrapper class that is used to construct a custom handler class."""

    delegate = None

    def setup(self):
        super().setup()
        self.delegate = self.DELEGATE_CLASS(self.rfile, self.wfile)

    def handle(self):
        try:
            self.delegate.start()
        except OSError as e:
            if os.name == 'nt':
                # Catch and pass on ConnectionResetError when parent process
                # dies
                # pylint: disable=no-member, undefined-variable
                if isinstance(e, WindowsError) and e.winerror == 10054:
                    pass

        self.SHUTDOWN_CALL()


def start_tcp_lang_server(bind_addr, port, window, check_parent_process):
    # if not issubclass(handler_class, PythonLSPServer):
    #     raise ValueError('Handler class must be an instance of PythonLSPServer')
    handler_class = PreviewServer

    def shutdown_server(check_parent_process, *args):
        # pylint: disable=unused-argument
        if check_parent_process:
            log.debug('Shutting down server')
            # Shutdown call must be done on a thread, to prevent deadlocks
            stop_thread = threading.Thread(target=server.shutdown)
            stop_thread.start()
        window.destroy()

    # Construct a custom wrapper class around the user's handler_class
    wrapper_class = type(
        handler_class.__name__ + 'Handler',
        (_StreamHandlerWrapper,),
        {'DELEGATE_CLASS': partial(handler_class,
                                   window=window,
                                   check_parent_process=check_parent_process),
         'SHUTDOWN_CALL': partial(shutdown_server, check_parent_process)}
    )

    server = socketserver.TCPServer((bind_addr, port), wrapper_class, bind_and_activate=False)
    server.allow_reuse_address = True

    try:
        server.server_bind()
        server.server_activate()
        log.info('Serving %s on (%s, %s)', handler_class.__name__, bind_addr, port)
        server.serve_forever()
    finally:
        log.info('Shutting down')
        server.server_close()


def start_io_lang_server(window, check_parent_process):
    handler_class = PreviewServer
    # if not issubclass(handler_class, PythonLSPServer):
    #     raise ValueError('Handler class must be an instance of PythonLSPServer')

    # binary stdin/out
    stdin, stdout = sys.stdin.buffer, sys.stdout.buffer
    rfile, wfile = stdin, stdout
    log.info('Starting %s IO language server', handler_class.__name__)
    server = handler_class(rfile, wfile, window, check_parent_process)
    server.start()

class PreviewServer(MethodDispatcher):
    def __init__(self, rx, tx, window, *args, **kwargs):
        self.window = window
        renderer = markshift.htmlrenderer.HtmlRenderer()
        self.parser = markshift.parser.Parser(renderer, use_tokenizer=True)

        # Setup an endpoint that dispatches to the ls, and writes server->client messages
        # back to the client websocket
        if rx is not None:
            self._jsonrpc_stream_reader = JsonRpcStreamReader(rx)
        else:
            self._jsonrpc_stream_reader = None

        if tx is not None:
            self._jsonrpc_stream_writer = JsonRpcStreamWriter(tx)
        else:
            self._jsonrpc_stream_writer = None

        self._endpoint = Endpoint(self, self._jsonrpc_stream_writer.write, max_workers=MAX_WORKERS)

    def start(self):
        """Entry point for the server."""
        self._jsonrpc_stream_reader.listen(self._endpoint.consume)

    def consume(self, message):
        """Entry point for consumer based server. Alternative to stream listeners."""
        # assuming message will be JSON
        self._endpoint.consume(message)

    def m_initialize(self, **kwargs):
        log.info("Got initialize params: %s", kwargs)
        return {}

    def m_show(self, **kwargs):
        log.info("showing window")
        self.window.show()
        return {}

    def m_hide(self, **kwargs):
        log.info("hiding window")
        self.window.hide()
        return {}

    def m_render_text(self, textDocument=None, **_kwargs):
        log.info("Opened text document %s", textDocument['uri'])
        tree = self.parser.parse(textDocument['content'].split('\n'))

        self.window.load_html(tree.render())

        # self.endpoint.notify('textDocument/publishDiagnostics', {
        #     'uri': textDocument['uri'],
        #     'diagnostics': [{
        #         'range': {
        #             'start': {'line': 0, 'character': 0},
        #             'end': {'line': 1, 'character': 0},
        #         },
        #         'message': 'Some very bad Python code',
        #         'severity': 1  # DiagnosticSeverity.Error
        #     }]
        # })


@click.command()
@click.option('--tcp', type=bool, default=False, is_flag=True)
@click.option('--logfile', type=click.Path(exists=False), default=None)
def main(tcp, logfile):
    rootlogger = logging.getLogger()
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    if logfile is not None:
        fileHandler = logging.FileHandler(logfile)
        fileHandler.setFormatter(logFormatter)
        rootlogger.addHandler(fileHandler)
    rootlogger.setLevel(logging.INFO)
    # consoleHandler = logging.StreamHandler()
    # consoleHandler.setFormatter(logFormatter)
    # rootlogger.addHandler(consoleHandler)

    window = webview.create_window('markshift_previewer', hidden=True)
    webview.start(start, [window, tcp], gui='qt')

def start(window, tcp):
    import time
    time.sleep(1)
    if tcp:
        start_tcp_lang_server("0.0.0.0", 7920, window, check_parent_process=True)
    else:
        start_io_lang_server(window, check_parent_process=True)


if __name__ == '__main__':
    main()
