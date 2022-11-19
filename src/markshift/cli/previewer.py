#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(''))
import click
import re
import threading
import logging
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
import markshift.htmlrenderer4preview

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
{{BODY}}
</body>
</html>
"""   


@click.command()
@click.option('--inputms', type=click.Path(exists=True), default=None)
@click.option('--logfile', type=click.Path(exists=False), default=None)
def main(inputms, logfile):
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

    window = webview.create_window('markshift_previewer', hidden=False)
    webview.start(start, (window, inputms), gui='qt')

def start(window, inputms):
    try:
        renderer = markshift.htmlrenderer4preview.HtmlRenderer4Preview()
        parser = markshift.parser.Parser(renderer)
        with open(inputms) as f:
            tree = parser.parse([l.rstrip('\n') for l in f.readlines()])
        window.load_html(template.replace('{{BODY}}', tree.render()))

    except Exception as e:
        log.error(e)
        window.destroy()
        raise e

if __name__ == '__main__':
    main()
