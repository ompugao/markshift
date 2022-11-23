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
import datetime
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

import networkx as nx

from pygls.lsp.methods import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                               TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN,
                               TEXT_DOCUMENT_DID_SAVE,
                               TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
                               INITIALIZED)
from pygls.lsp.types import (CompletionItem, CompletionList, CompletionOptions,
                             CompletionItemKind,
                             CompletionParams, ConfigurationItem,
                             ConfigurationParams, Diagnostic,
                             DidChangeTextDocumentParams,
                             DidCloseTextDocumentParams,
                             DidOpenTextDocumentParams,
                             DidSaveTextDocumentParams,
                             InitializedParams,
                             MessageType, Position,
                             Range, Registration, RegistrationParams,
                             SemanticTokens, SemanticTokensLegend, SemanticTokensParams,
                             Unregistration, UnregistrationParams,
                             WorkspaceEdit)
from pygls.lsp.types.basic_structures import (WorkDoneProgressBegin,
                                              WorkDoneProgressEnd,
                                              WorkDoneProgressReport)
from pygls.server import LanguageServer
from pygls import uris

from markshift.exception import ParserError
import markshift.parser
# import markshift.htmlrenderer
import markshift.htmlrenderer4preview
from .zotero import zotero_comp
from markshift.element import WikiLinkElement
import urllib
import glob
import pathlib

log = logging.getLogger(__name__)


file_ext = '.ms'

def retrieve_asset(name, dir='assets'):
    if getattr(sys, 'frozen', False):
        # print('sys.frozen:', sys.frozen)
        # print('sys.executable:', sys.executable)
        # print('sys._MEIPASS:', sys._MEIPASS)

        folder_of_executable = os.path.dirname(sys.executable)
        if os.path.samefile(folder_of_executable, sys._MEIPASS):
            base_path = os.path.dirname(folder_of_executable)
        else:
            base_path = folder_of_executable

        assets_path = os.path.join(sys._MEIPASS, dir)
    else:
        assets_path = str(pathlib.Path( __file__ ).parent.parent.parent.parent.parent.absolute() / dir)
    return os.path.join(assets_path, name)

class MarkshiftLanguageServer(LanguageServer):
    CMD_SHOW_PREVIEWER = 'showPreviewer'
    CMD_HIDE_PREVIEWER = 'hidePreviewer'
    CMD_FORCE_REDRAW = 'forceRedraw'
    CMD_INSERT_IMAGE_FROM_CLIPBOARD = 'insertImageFromClipboard'
    CMD_PROGRESS = 'progress'
    CMD_REGISTER_COMPLETIONS = 'registerCompletions'
    CMD_SHOW_CONFIGURATION_ASYNC = 'showConfigurationAsync'
    CMD_SHOW_CONFIGURATION_CALLBACK = 'showConfigurationCallback'
    CMD_SHOW_CONFIGURATION_THREAD = 'showConfigurationThread'
    CMD_UNREGISTER_COMPLETIONS = 'unregisterCompletions'

    CONFIGURATION_SECTION = 'MarkshiftLanguageServer'

    def __init__(self, *args):
        super().__init__(*args)

        self.previewer = None
        self.zotero_path = None

        renderer = markshift.htmlrenderer4preview.HtmlRenderer4Preview()
        self.parser = markshift.parser.Parser(renderer)

        self._initialize_assets()


        self.wikilink_graph = nx.DiGraph()
        self.managed_docs_wikilinks = dict()

    def _initialize_assets(self):
        css = StringIO()
        with open(retrieve_asset('katex/katex.css')) as f:
            css.write(f.read())
        with open(retrieve_asset('highlightjs/styles/github-dark.min.css')) as f:
            css.write(f.read())
        with open(retrieve_asset('dark-theme.css')) as f:
            css.write(f.read())
        css.write("""
            .empty-line{
                list-style-type: none;
            }
            .image {
                vertical-align: top;
            }
            ul {
                margin: 4px;
            }
            body {
                font-size: 24px;
                line-height: 1.5em;
            }
            .main-content {
                margin: 20px;
            }
            .code-inline {
                background-color: rgba(208, 208, 208, 0.08);
                padding: 0.06em;
                border-radius: 0.2em;
            }
            pre {
                tab-size: 4;
            }
            blockquote {
                background: #4c4c4c5c;
                padding: 0.5em 20px 0.5em 20px;
                margin-block-start: 0.5em;
                margin-block-end: 0.5em;
                margin-inline-start: 30px;
                margin-inline-end: 30px;
                color: #bbb;
            }
            .katex-version {display: none;}
            .katex-version::after {content:"0.10.2 or earlier";}
            """)
        self.css = css.getvalue()

        js = StringIO()
        with open(retrieve_asset('highlightjs/highlight.min.js')) as f:
            js.write(f.read())
        with open(retrieve_asset('katex/katex.min.js')) as f:
            js.write(f.read())
        with open(retrieve_asset('katex/contrib/auto-render.min.js')) as f:
            js.write(f.read())
        js.write("""
        function on_wikilink_click(pagename) {
            pywebview.api.on_wikilink_click(pagename)
        }
        hljs.highlightAll();
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
        """)
        self.js = js.getvalue()

    def set_previewer(self, previewer):
        self.previewer = previewer

    def set_zotero_path(self, zotero_path):
        self.zotero_path = zotero_path

    def show_previewer(self, ):
        self.previewer.show()

    def hide_previewer(self, ):
        self.previewer.hide()

    def render_content(self, title, content, backlinks=None):
        htmlio = StringIO()
        htmlio.write("<!DOCTYPE html><html><head><style>")
        htmlio.write(self.css)
        htmlio.write("</style>")
        htmlio.write('<script type="text/javascript">')
        htmlio.write(self.js)
        htmlio.write('</script></head>')
        htmlio.write('<body>')
        htmlio.write('<div class="main-content">')
        # htmlio.write(f'<h1>{title}</h1>')
        htmlio.write(content)
        if backlinks:
            htmlio.write('<hr id="hr-footer" style="width:95%; margin-top: 0.5em; margin-bottom: 0.5em; background-color: #959595;"/>')
            icon_uri = uris.from_fs_path(retrieve_asset('img/cited_icon.png'))
            htmlio.write(f'<img class="icon-cited" src="{icon_uri}" alt="This page is cited from the followings:" width=15 height=15 style="vertical-align: middle;"/>')
            htmlio.write('<ul id="backlink-list" style="padding-inline-start: 20px">')
            for backlink in backlinks:
                htmlio.write(f'<li><a href=\'javascript:on_wikilink_click("{backlink}\");\'>{backlink}</a></li>')
            htmlio.write('</ul>')
        htmlio.write('</div></body></html>')
        self.previewer.load_html(htmlio.getvalue())
        self.previewer.set_title(title)

    def parse_lines(self, lines):
        tree = self.parser.parse(lines)
        return tree

    def gather_wiki_links(self, tree):
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
        self.previewer.destroy()


msls_server = MarkshiftLanguageServer('pygls-json-example', 'v0.1')

def _render_document(ls, uri):
    # ls.show_message_log('Rendering text...')
    text_doc = ls.workspace.get_document(uri)

    lines = text_doc.source.splitlines(keepends=False)
    try:
        tree = msls_server.parse_lines(lines)
        backlinks = [linked for linked, _ in msls_server.wikilink_graph.in_edges(uri_to_link_name(uri))]
        path = uris.urlparse(uri)[2]
        
        msls_server.render_content(pathlib.Path(path).name, tree.render(), backlinks)
    except ParserError as e:
        msg = str(e)
        col = e.column
        line = e.line

        d = Diagnostic(
            range=Range(
                start=Position(line=line - 1, character=col - 1),
                end=Position(line=line - 1, character=col)
            ),
            message=msg,
            source=type(msls_server).__name__
        )
        ls.publish_diagnostics(uri, [d])
        return None
    except Exception as e:
        log.error(e)
        return None

    # no error
    ls.publish_diagnostics(uri, [])
    return tree


@msls_server.feature(COMPLETION, CompletionOptions(trigger_characters=['[', '@']))
def completions(params: Optional[CompletionParams] = None) -> CompletionList:
    """Returns completion items."""

    items = []
    if params is not None:
        doc = msls_server.lsp.workspace.get_document(params.text_document.uri)
        l = doc.lines[params.position.line]
        c = params.position.character

        if l[c-1] == '@':
            return CompletionList(
                is_incomplete=False,
                items = [CompletionItem(label=command, kind=CompletionItemKind.Function,
                                         filter_text=command, insert_text=command) for command in ['code', 'math', 'table', 'quote']],
            )

        lindex = l[:c].rfind('[')
        rindex = l[:c].rfind(']')
        if lindex < 0 or lindex < rindex:
            items = []
        #else:
        elif lindex == c-1:  # complete only when typed '['
            # typedchrs = l[index+1:c]
            # TODO fuzzy match?
            # items = [CompletionItem(label=wikilink) for wikilink in msls_server.wikilink_graph.nodes() if wikilink.startswith(typedchrs)]
            items = [CompletionItem(label=wikilink, kind=CompletionItemKind.Reference) for wikilink in msls_server.wikilink_graph.nodes()]
            if msls_server.zotero_path is not None:
                zoteroitems = zotero_comp(msls_server.lsp, msls_server.zotero_path)
                if zoteroitems is not None:
                    items.extend([CompletionItem(label='Z: '+title, kind=CompletionItemKind.Reference, insert_text=inserttext) for title, inserttext in zoteroitems])

    else:
        items = [CompletionItem(label=wikilink, kind=CompletionItemKind.Reference) for wikilink in msls_server.wikilink_graph.nodes()]
    return CompletionList(
        is_incomplete=False,
        items = items,
    )


@msls_server.command(MarkshiftLanguageServer.CMD_SHOW_PREVIEWER)
async def show_previewer(ls, *args):
    ls.show_message(f'showing previewer...')
    msls_server.show_previewer()

@msls_server.command(MarkshiftLanguageServer.CMD_HIDE_PREVIEWER)
async def hide_previewer(ls, *args):
    ls.show_message(f'hiding previewer...')
    msls_server.hide_previewer()

@msls_server.command(MarkshiftLanguageServer.CMD_FORCE_REDRAW)
async def force_redraw(ls, args):
    log.debug('args: %s'%args)
    uri = args[0]
    _render_document(ls, uri)

# @msls_server.command(MarkshiftLanguageServer.CMD_INSERT_IMAGE_FROM_CLIPBOARD)
# async def insert_image_from_clipboard(ls, *args):
#     from qtpy.QtWidgets import QApplication
#     app = QApplication.instance()
#     if app is None:
#         log.info("no qt instance")
#         return
#     clip = app.clipboard()
#     if not clip.mimeData().hasImage():
#         log.info("image is not in clipboard")
#         return
#     text = clip.text()
#     if text == '':
#         text = 'img_' + datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
#     fullfilename = str(pathlib.Path(msls_server.server.lsp.workspace.root_path) / 'assets' / (text + '.png'))
#     clip.image().save(fullfilename)
#     
#     'assets' / (text + '.png')
#     msls_server.apply_edit



@msls_server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    tree = _render_document(ls, params.text_document.uri)
    if tree is None:
        return

    wikilinks = set([elm.link for elm in msls_server.gather_wiki_links(tree)])
    page = uri_to_link_name(params.text_document.uri)
    update_wikilinks(page, wikilinks)


@msls_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: MarkshiftLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    server.show_message('Text Document Did Close')
    msls_server.render_body('', '')


@msls_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message('Text Document Did Open')
    tree = _render_document(ls, params.text_document.uri)
    page = uri_to_link_name(params.text_document.uri)
    wikilinks = set([elm.link for elm in msls_server.gather_wiki_links(tree)])
    page = uri_to_link_name(params.text_document.uri)
    update_wikilinks(page, wikilinks)

@msls_server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls, params: DidSaveTextDocumentParams):
    pass

def update_wikilinks(page, newlinks):
    oldlinks = set([v for k, v in msls_server.wikilink_graph.out_edges(page)])
    newlinks = set(newlinks)
    for wikilink in (newlinks - oldlinks):
        msls_server.wikilink_graph.add_edge(page, wikilink)
    for wikilink in (oldlinks - newlinks):
        msls_server.wikilink_graph.remove_edge(page, wikilink)
        # Remove node if
        # 1. the node is not an existing file
        # 2. the node does not have any in-edges
        no_in_edges = (len(msls_server.wikilink_graph.in_edges(wikilink)) == 0)
        if no_in_edges and not (pathlib.Path(msls_server.lsp.workspace.root_path) / (wikilink + file_ext)).exists():
            log.info(f'Node "{wikilink}" disappears.')
            msls_server.wikilink_graph.remove_node(wikilink)


def uri_to_link_name(uri):
    return path_to_link_name(urllib.parse.unquote(uri))

def path_to_link_name(path):
    return pathlib.Path(path).name.removesuffix(file_ext)

@msls_server.feature(INITIALIZED)
async def lsp_initialized(ls, params: InitializedParams):
    """Lsp is initialized. The server will start scanning files"""
    if not ls.workspace.is_local():
        return
    ls.show_message('Scanning started')
    token = 'scanning_token'
    await ls.progress.create_async(token)

    ls.progress.begin(token, WorkDoneProgressBegin(title='Scanning', percentage=0))
    files = glob.glob(str(pathlib.Path(ls.workspace.root_path) / ('**/*' + file_ext)), recursive=True)
    for ifile, file in enumerate(files):
        with open(file) as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
        # if True:
        try:
            tree = msls_server.parse_lines(lines)
            wikilinks = msls_server.gather_wiki_links(tree)
            name = path_to_link_name(file)
            msls_server.wikilink_graph.add_edges_from([(name, e.link) for e in wikilinks])
        except Exception as e:
            log.error('Failed to extract wiklinks from %s'%file)
            log.error(e)
            continue

        # ls.show_message_log(f'{pathlib.Path(file).name} has {len(wikilinks)} links')
        percent = ifile*100.0/len(files)
        ls.progress.report(
            token,
            WorkDoneProgressReport(message=f'{pathlib.Path(file).name}', percentage = int(percent)),
        )
        await asyncio.sleep(0.1)
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

