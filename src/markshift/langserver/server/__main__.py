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

from .server import msls_server, Api


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
    parser.add_argument(
        "--logfile", type=str, default='',
        help="path to log file"
    )
    parser.add_argument(
        "--always_on_top", action='store_true',
        help=""
    )
    parser.add_argument(
        "--hidden_on_boot", action='store_true',
        help="do not show a preview window when started"
    )
    parser.add_argument(
        "--never_steal_focus", action='store_true',
        help="set a previewer not to steal focus"
    )

def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if len(args.logfile) > 0:
        logging.basicConfig(filename=args.logfile, level=logging.DEBUG, filemode="w")
    api = Api(msls_server)
    msls_server.window = webview.create_window('markshift_previewer', js_api=api, hidden=True, text_select=True, on_top=args.always_on_top)
    webview.start(_start, args, gui='qt')
    # _start(args)

def _start(args):
    if args.never_steal_focus:
        # do not steal focus
        import time
        time.sleep(1)

        from qtpy.QtCore import Qt
        view = msls_server.window.gui.BrowserView.instances['master']
        view.setWindowFlag(Qt.WindowDoesNotAcceptFocus)
        time.sleep(0.1)

    if not args.hidden_on_boot:
        msls_server.window.show()

    if args.tcp:
        msls_server.start_tcp(args.host, args.port)
    elif args.ws:
        msls_server.start_ws(args.host, args.port)
    else:
        msls_server.start_io()


if __name__ == '__main__':
    main()
