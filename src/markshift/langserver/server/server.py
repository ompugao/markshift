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
import sys, os
sys.path.append(os.path.abspath(''))
import re
import threading
import logging
import pathlib
from functools import partial
try:
    import ujson as json
except Exception:  # pylint: disable=broad-except
    import json
from io import StringIO

import asyncio
# import json
import re
import time
import uuid
from typing import Optional

from pygls.lsp.methods import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                               TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN, 
                               TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
                               INITIALIZED)
from pygls.lsp.types import (CompletionItem, CompletionList, CompletionOptions,
                             CompletionParams, ConfigurationItem,
                             ConfigurationParams, Diagnostic,
                             DidChangeTextDocumentParams,
                             DidCloseTextDocumentParams,
                             DidOpenTextDocumentParams,
                             InitializedParams,
                             MessageType, Position,
                             Range, Registration, RegistrationParams,
                             SemanticTokens, SemanticTokensLegend, SemanticTokensParams,
                             Unregistration, UnregistrationParams)
from pygls.lsp.types.basic_structures import (WorkDoneProgressBegin,
                                              WorkDoneProgressEnd,
                                              WorkDoneProgressReport)
from pygls.server import LanguageServer

# import webview
import markshift.parser
# import markshift.htmlrenderer
import markshift.htmlrenderer4preview
from markshift.element import WikiLinkElement
import glob
import pathlib

log = logging.getLogger(__name__)

class MarkshiftLanguageServer(LanguageServer):
    CMD_SHOW_PREVIEWER = 'showPreviewer'
    CMD_HIDE_PREVIEWER = 'hidePreviewer'
    CMD_FORCE_REDRAW = 'forceRedraw'
    CMD_PROGRESS = 'progress'
    CMD_REGISTER_COMPLETIONS = 'registerCompletions'
    CMD_SHOW_CONFIGURATION_ASYNC = 'showConfigurationAsync'
    CMD_SHOW_CONFIGURATION_CALLBACK = 'showConfigurationCallback'
    CMD_SHOW_CONFIGURATION_THREAD = 'showConfigurationThread'
    CMD_UNREGISTER_COMPLETIONS = 'unregisterCompletions'

    CONFIGURATION_SECTION = 'MarkshiftLanguageServer'

    def __init__(self, *args):
        super().__init__(*args)

        self.window = None

        renderer = markshift.htmlrenderer4preview.HtmlRenderer4Preview()
        self.parser = markshift.parser.Parser(renderer)


    # def start_io(self, stdin=None, stdout=None):
    #     super().start_io()
    #     self._start_hook()

    # def start_pyodide(self):
    #     super().start_pyodide()
    #     self._start_hook()

    # def start_tcp(self, host, port):
    #     super().start_tcp()
    #     self._start_hook()

    # def start_ws(self, host, port):
    #     super().start_ws()
    #     self._start_hook()

    def load_stuff(self,):
        if self.window is not None:
            script_path = pathlib.Path( __file__ ).parent.absolute()

            css = StringIO()
            with open(script_path / '../../../../assets/katex/katex.css') as f:
                css.write(f.read())
            with open(script_path / '../../../../assets/highlightjs/styles/github.min.css') as f:
                css.write(f.read())
            with open(script_path / '../../../../assets/github-markdown.min.css') as f:
                css.write(f.read())
            css.write("""
                .empty-line{
                    list-style-type: none;
                }
                .image {
                    vertical-align: top; 
                }
                """)
            self.window.load_css(css.getvalue())

            js = StringIO()
            with open(script_path / "../../../../assets/highlightjs/highlight.min.js") as f:
                js.write(f.read())
            with open(script_path / "../../../../assets/katex/katex.min.js") as f:
                js.write(f.read())
            with open(script_path / "../../../../assets/katex/contrib/auto-render.min.js") as f:
                js.write(f.read())
            js.write("""
            function on_wikilink_click(pagename) {
                pywebview.api.on_wikilink_click(pagename)
            }
            hljs.highlightAll();
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
            """)
            self.window.evaluate_js(js.getvalue())

            


    def show(self, ):
        if self.window is not None:
            self.window.show()

    def hide(self, ):
        if self.window is not None:
            self.window.hide()

    def render_lines(self, lines):
        tree = self.parser.parse(lines)
        if self.window is not None:
            # self.window.load_html(template.replace('{{BODY}}', tree.render()))
            self.window.load_html("<!DOCTYPE html>" + tree.render())
            self.load_stuff()

    def scan_wiki_links(self, lines):
        tree = self.parser.parse(lines)
        ret = []
        self._gather_wiki_links(tree, ret)
        return ret

    def _gather_wiki_links(self, tree, ret):
        if type(tree) == WikiLinkElement:
            ret.append(tree)
        for e in tree.child_elements:
            self._gather_wiki_links(e, ret)
        for e in tree.child_lines:
            self._gather_wiki_links(e, ret)

    def shutdown(self,):
        super().shutdown()
        if self.window is not None:
            self.window.destroy()


msls_server = MarkshiftLanguageServer('pygls-json-example', 'v0.1')

def _validate(ls, params):
    ls.show_message_log('Validating json...')

    text_doc = ls.workspace.get_document(params.text_document.uri)

    source = text_doc.source
    diagnostics = _validate_json(source) if source else []

    ls.publish_diagnostics(text_doc.uri, diagnostics)


def _validate_json(source):
    """Validates json file."""
    diagnostics = []

    try:
        json.loads(source)
    except JSONDecodeError as err:
        msg = err.msg
        col = err.colno
        line = err.lineno

        d = Diagnostic(
            range=Range(
                start=Position(line=line - 1, character=col - 1),
                end=Position(line=line - 1, character=col)
            ),
            message=msg,
            source=type(msls_server).__name__
        )

        diagnostics.append(d)

    return diagnostics

def _render_document(ls, uri):
    # ls.show_message_log('Rendering text...')
    text_doc = ls.workspace.get_document(uri)

    lines = text_doc.source.splitlines(keepends=False)
    diagnostics = []
    try:
        msls_server.render_lines(lines)
    except Exception as e:
        pass
    # diagnostics = _validate_json(source) if source else []

    ls.publish_diagnostics(uri, diagnostics)


@msls_server.feature(COMPLETION, CompletionOptions(trigger_characters=[',']))
def completions(params: Optional[CompletionParams] = None) -> CompletionList:
    """Returns completion items."""
    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(label='"'),
            CompletionItem(label='['),
            CompletionItem(label=']'),
            CompletionItem(label='{'),
            CompletionItem(label='}'),
        ]
    )


@msls_server.command(MarkshiftLanguageServer.CMD_SHOW_PREVIEWER)
async def show_previewer(ls, *args):
    ls.show_message(f'showing previewer...')
    msls_server.show()

@msls_server.command(MarkshiftLanguageServer.CMD_HIDE_PREVIEWER)
async def hide_previewer(ls, *args):
    ls.show_message(f'hiding previewer...')
    msls_server.hide()

@msls_server.command(MarkshiftLanguageServer.CMD_FORCE_REDRAW)
async def force_redraw(ls, args):
    log.debug('args: %s'%args)
    uri = args[0]
    _render_document(ls, uri)


@msls_server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    # _validate(ls, params)
    _render_document(ls, params.text_document.uri)



@msls_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: MarkshiftLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    server.show_message('Text Document Did Close')
    msls_server.render_lines([])


@msls_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message('Text Document Did Open')
    # _validate(ls, params)
    _render_document(ls, params.text_document.uri)

@msls_server.feature(INITIALIZED)
async def lsp_initialized(ls, params: InitializedParams):
    """Lsp is initialized. The server will scan files"""
    if not ls.workspace.is_local():
        return
    ls.show_message('Scanning started')
    token = 'scanning_token'
    await ls.progress.create_async(token)

    ls.progress.begin(token, WorkDoneProgressBegin(title='Scanning', percentage=0))
    files = glob.glob(str(pathlib.Path(ls.workspace.root_path) / '**/*.ms'), recursive=True)
    for ifile, file in enumerate(files):
        with open(file) as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
        wikilinks = msls_server.scan_wiki_links(lines)
        ls.show_message(f'{pathlib.Path(file).name}: {len(wikilinks)}')

        percent = ifile*100.0/len(files)
        ls.progress.report(
            token,
            WorkDoneProgressReport(message=f'{percent}%', percentage = int(percent)),
        )
        # await asyncio.sleep(2)
    ls.progress.end(token, WorkDoneProgressEnd(message='Finished'))


@msls_server.feature(
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
    SemanticTokensLegend(
        token_types = ["operator"],
        token_modifiers = []
    )
)
def semantic_tokens(ls: MarkshiftLanguageServer, params: SemanticTokensParams):
    """See https://microsoft.github.io/language-server-protocol/specification#textDocument_semanticTokens
    for details on how semantic tokens are encoded."""
    
    TOKENS = re.compile('".*"(?=:)')
    
    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)

    last_line = 0
    last_start = 0

    data = []

    for lineno, line in enumerate(doc.lines):
        last_start = 0

        for match in TOKENS.finditer(line):
            start, end = match.span()
            data += [
                (lineno - last_line),
                (start - last_start),
                (end - start),
                0, 
                0
            ]

            last_line = lineno
            last_start = start

    return SemanticTokens(data=data)



@msls_server.command(MarkshiftLanguageServer.CMD_PROGRESS)
async def progress(ls: MarkshiftLanguageServer, *args):
    """Create and start the progress on the client."""
    token = 'token'
    # Create
    await ls.progress.create_async(token)
    # Begin
    ls.progress.begin(token, WorkDoneProgressBegin(title='Indexing', percentage=0))
    # Report
    for i in range(1, 10):
        ls.progress.report(
            token,
            WorkDoneProgressReport(message=f'{i * 10}%', percentage= i * 10),
        )
        await asyncio.sleep(2)
    # End
    ls.progress.end(token, WorkDoneProgressEnd(message='Finished'))


@msls_server.command(MarkshiftLanguageServer.CMD_REGISTER_COMPLETIONS)
async def register_completions(ls: MarkshiftLanguageServer, *args):
    """Register completions method on the client."""
    params = RegistrationParams(registrations=[
                Registration(
                    id=str(uuid.uuid4()),
                    method=COMPLETION,
                    register_options={"triggerCharacters": "[':']"})
             ])
    response = await ls.register_capability_async(params)
    if response is None:
        ls.show_message('Successfully registered completions method')
    else:
        ls.show_message('Error happened during completions registration.',
                        MessageType.Error)


@msls_server.command(MarkshiftLanguageServer.CMD_SHOW_CONFIGURATION_ASYNC)
async def show_configuration_async(ls: MarkshiftLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using coroutines."""
    try:
        config = await ls.get_configuration_async(
            ConfigurationParams(items=[
                ConfigurationItem(
                    scope_uri='',
                    section=MarkshiftLanguageServer.CONFIGURATION_SECTION)
        ]))

        example_config = config[0].get('exampleConfiguration')

        ls.show_message(f'jsonServer.exampleConfiguration value: {example_config}')

    except Exception as e:
        ls.show_message_log(f'Error ocurred: {e}')


@msls_server.command(MarkshiftLanguageServer.CMD_SHOW_CONFIGURATION_CALLBACK)
def show_configuration_callback(ls: MarkshiftLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using callback."""
    def _config_callback(config):
        try:
            example_config = config[0].get('exampleConfiguration')

            ls.show_message(f'jsonServer.exampleConfiguration value: {example_config}')

        except Exception as e:
            ls.show_message_log(f'Error ocurred: {e}')

    ls.get_configuration(ConfigurationParams(items=[
        ConfigurationItem(
            scope_uri='',
            section=MarkshiftLanguageServer.CONFIGURATION_SECTION)
    ]), _config_callback)


@msls_server.thread()
@msls_server.command(MarkshiftLanguageServer.CMD_SHOW_CONFIGURATION_THREAD)
def show_configuration_thread(ls: MarkshiftLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using thread pool."""
    try:
        config = ls.get_configuration(ConfigurationParams(items=[
            ConfigurationItem(
                scope_uri='',
                section=MarkshiftLanguageServer.CONFIGURATION_SECTION)
        ])).result(2)

        example_config = config[0].get('exampleConfiguration')

        ls.show_message(f'jsonServer.exampleConfiguration value: {example_config}')

    except Exception as e:
        ls.show_message_log(f'Error ocurred: {e}')


@msls_server.command(MarkshiftLanguageServer.CMD_UNREGISTER_COMPLETIONS)
async def unregister_completions(ls: MarkshiftLanguageServer, *args):
    """Unregister completions method on the client."""
    params = UnregistrationParams(unregisterations=[
        Unregistration(id=str(uuid.uuid4()), method=COMPLETION)
    ])
    response = await ls.unregister_capability_async(params)
    if response is None:
        ls.show_message('Successfully unregistered completions method')
    else:
        ls.show_message('Error happened during completions unregistration.',
                        MessageType.Error)

