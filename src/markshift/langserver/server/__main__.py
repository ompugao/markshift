# -*- coding: utf-8 -*-
############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License")           #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http: // www.apache.org/licenses/LICENSE-2.0                         #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
import argparse
import logging
import webview

from .server import msls_server

logging.basicConfig(filename="msls.log", level=logging.DEBUG, filemode="w")

log = logging.getLogger(__name__)

def add_arguments(parser):
    parser.description = "markshift language server"

    parser.add_argument(
        "--tcp", action="store_true",
        help="Use TCP server"
    )
    parser.add_argument(
        "--ws", action="store_true",
        help="Use WebSocket server"
    )
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Bind to this address"
    )
    parser.add_argument(
        "--port", type=int, default=2087,
        help="Bind to this port"
    )

from pygls.lsp.types.window import ShowDocumentParams
from pygls.lsp.types import (Position, Range)

class Api(object):
    def __init__(self,):
        pass
    def on_wikilink_click(self, pagename):
        pagename = pagename.removesuffix('.ms') + ".ms"  # ensure suffix
        params = ShowDocumentParams(
                uri = msls_server.lsp.workspace.root_uri + '/' + pagename)
        # range = Range(start = Position(line = 3, character = 0),
        #               end = Position(line = 10, character = 0))
        # params.selection = range
        log.info(params.uri)
        msls_server.show_document(params)

def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    api = Api()
    msls_server.window = webview.create_window('markshift_previewer', js_api=api, hidden=True)
    webview.start(_start, args, gui='qt')
    # _start(args)

def _start(args):
    import time
    time.sleep(1)

    # do not steal focus
    # from qtpy.QtCore import Qt
    # view = msls_server.window.gui.BrowserView.instances['master']
    # view.setWindowFlag(Qt.WindowDoesNotAcceptFocus)
    # time.sleep(0.1)
    msls_server.window.show()

    if args.tcp:
        msls_server.start_tcp(args.host, args.port)
    elif args.ws:
        msls_server.start_ws(args.host, args.port)
    else:
        msls_server.start_io()


if __name__ == '__main__':
    main()
