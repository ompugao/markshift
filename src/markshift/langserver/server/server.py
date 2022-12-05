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
import logging
import pathlib
from io import StringIO
import asyncio
import time
import uuid
from typing import Optional
import tempfile

import networkx as nx

from pygls.lsp.methods import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                               TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN,
                               TEXT_DOCUMENT_DID_SAVE,
                               TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
                               INITIALIZED,
                               DOCUMENT_LINK)
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
                             WorkspaceEdit,
                             DocumentLink,
                             DocumentLinkOptions,
                             DocumentLinkParams,
                             ShowDocumentParams)
from pygls.lsp.types.basic_structures import (WorkDoneProgressBegin,
                                              WorkDoneProgressEnd,
                                              WorkDoneProgressReport,
                                              DiagnosticSeverity)
from pygls.server import LanguageServer
from pygls import uris

from markshift.exception import ParserError
import markshift.parser
# import markshift.htmlrenderer
import markshift.markdownrenderer
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
    CMD_EXPORT_MARKDOWN = 'exportMarkdown'
    CMD_INSERT_IMAGE_FROM_CLIPBOARD = 'insertImageFromClipboard'
    CMD_REGISTER_COMPLETIONS = 'registerCompletions'
    CMD_SHOW_CONFIGURATION_ASYNC = 'showConfigurationAsync'
    CMD_UNREGISTER_COMPLETIONS = 'unregisterCompletions'

    CONFIGURATION_SECTION = 'MarkshiftLanguageServer'

    def __init__(self, *args):
        super().__init__(*args)

        self.previewer = None
        self.zotero_path = None

        renderer = markshift.htmlrenderer4preview.HtmlRenderer4Preview()
        self.parser = markshift.parser.Parser(renderer)

        self.markdown_parser = markshift.parser.Parser(markshift.markdownrenderer.MarkdownRenderer())

        self._initialize_assets()


        self.wikilink_graph = nx.DiGraph()
        self.managed_docs_wikilinks = dict()

    def _initialize_assets(self):
        css = StringIO()
        with open(retrieve_asset('katex/katex.css')) as f:
            css.write(f.read())
        with open(retrieve_asset('highlightjs/styles/github-dark.min.css')) as f:
            css.write(f.read())
        self.css = css.getvalue()

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
        htmlio.write('<div class="main-content">')
        htmlio.write(content)
        if backlinks:
            htmlio.write('<hr id="hr-footer" style="width:95%; margin-top: 0.5em; margin-bottom: 0.5em; background-color: #959595;"/>')
            icon_uri = uris.from_fs_path(retrieve_asset('img/cited_icon.png'))
            htmlio.write(f'<img class="icon-cited" src="{icon_uri}" alt="This page is cited from the followings:" width=15 height=15 style="vertical-align: middle;"/>')
            htmlio.write('<ul id="backlink-list" style="padding-inline-start: 20px">')
            for backlink in backlinks:
                htmlio.write(f'<li><a href=\'javascript:pywebview.api.on_wikilink_click("{backlink}\");\'>{backlink}</a></li>')
            htmlio.write('</ul>')
        htmlio.write('</div>')

        localhtml = pathlib.Path(retrieve_asset('gui/index.html'))
        if self.previewer.get_current_url() != localhtml.as_uri():
            self.previewer.load_url(localhtml)
            self.previewer.load_css(self.css)
        # log.info('current_url: %s'%self.previewer.get_current_url())
        # log.info('localhtml: %s'%localhtml)
        self.previewer.set_title(title)
        content = repr(htmlio.getvalue())
        self.previewer.evaluate_js("""
            if (!window.pywebview.state) {
              window.addEventListener('pywebview_state_ready', function() {
                 window.pywebview.state.setContent(%s)
              });
            } else {
              window.pywebview.state.setContent(%s);
            }"""%(content, content))

    def parse_lines(self, lines, return_warnings=False):
        tree, warnings = self.parser.parse(lines, return_warnings=True)
        if return_warnings:
            return tree, warnings
        return tree

    def gather_wiki_elements(self, tree):
        ret = []
        self._gather_wiki_elements(tree, ret)
        return ret

    def _gather_wiki_elements(self, tree, ret):
        if type(tree) == WikiLinkElement:
            ret.append(tree)
        for e in tree.child_elements:
            self._gather_wiki_elements(e, ret)
        for e in tree.child_lines:
            self._gather_wiki_elements(e, ret)

    def shutdown(self,):
        super().shutdown()
        self.previewer.destroy()


msls_server = MarkshiftLanguageServer('markshift-language-server', 'v0.1')

def _render_document(ls, uri):
    # ls.show_message_log('Rendering text...')
    text_doc = ls.workspace.get_document(uri)

    path = uris.urlparse(uri)[2]
    name = pathlib.Path(path).name
    lines = text_doc.source.splitlines(keepends=False)
    try:
        tree, warnings = msls_server.parse_lines(lines, return_warnings=True)
        backlinks = [linked for linked, _ in msls_server.wikilink_graph.in_edges(uri_to_link_name(uri))]
        wikielems = msls_server.gather_wiki_elements(tree)
        
        msls_server.render_content(name, tree.render(), backlinks)
        diags = []
        for w in warnings:
            line = w.line
            col = w.column
            msg = str(w)
            d = Diagnostic(
                range=Range(
                    start=Position(line=line - 1, character=col - 1),
                    end=Position(line=line - 1, character=col)
                ),
                message=msg,
                source=type(msls_server).__name__,
                severity=DiagnosticSeverity.Warning
            )
            diags.append(d)
        ls.publish_diagnostics(uri, diags)
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
        # msls_server.render_content(name, '', [])
        return None
    except Exception as e:
        log.error(e)
        ls.show_message(f'Unhandled Error: {str(e)}')
        # set no error
        ls.publish_diagnostics(uri, [])
        raise e

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
                                         filter_text=command, insert_text=command) for command in ['code', 'math', 'table', 'quote', 'img']],
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

@msls_server.command(MarkshiftLanguageServer.CMD_EXPORT_MARKDOWN)
async def export_markdown(ls, args):
    log.debug('args: %s'%args)
    uri = args[0]

    text_doc = ls.workspace.get_document(uri)
    lines = text_doc.source.splitlines(keepends=False)
    text = msls_server.markdown_parser.parse(lines).render()

    name = str(pathlib.Path(uris.to_fs_path(uri)).name).removesuffix('.ms')
    with tempfile.NamedTemporaryFile(mode='w', prefix=name, suffix='.md', delete=False) as f:
        mduri = uris.from_fs_path(f.name)
        f.write(text)
    params = ShowDocumentParams(
            uri = mduri)
    msls_server.show_document(params)

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
    wikielems = msls_server.gather_wiki_elements(tree)
    page = uri_to_link_name(params.text_document.uri)
    update_wikilink_connections(page, wikielems)
    update_wikilink_node_info(page, wikielems)


@msls_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: MarkshiftLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    msls_server.render_body('', '')


@msls_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    tree = _render_document(ls, params.text_document.uri)
    if tree is None:
        return
    wikielems = msls_server.gather_wiki_elements(tree)
    page = uri_to_link_name(params.text_document.uri)
    update_wikilink_connections(page, wikielems)
    update_wikilink_node_info(page, wikielems)

@msls_server.feature(TEXT_DOCUMENT_DID_SAVE)
async def did_save(ls, params: DidSaveTextDocumentParams):
    pass


def _wikielem_to_dict(wikielem,):
    return {'link': wikielem.link,
            'line': wikielem.line,
            'column': wikielem.column,
            'end_line': wikielem.end_line,
            'end_column': wikielem.end_column}

def update_wikilink_node_info(page, wikielems):
    data = []
    for e in wikielems:
        data.append(_wikielem_to_dict(e))
    msls_server.wikilink_graph.add_node(page)
    msls_server.wikilink_graph.nodes[page]['wikilinks'] = data


def update_wikilink_connections(page, wikielems):
    newlinks = set([elm.link for elm in wikielems])

    oldlinks = set([v for k, v in msls_server.wikilink_graph.out_edges(page)])
    newlinks = set(newlinks)
    msls_server.wikilink_graph.add_node(page)
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
        with open(file, encoding='utf-8') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]
        # if True:
        try:
            tree = msls_server.parse_lines(lines)
            wikilinks = msls_server.gather_wiki_elements(tree)
            name = path_to_link_name(file)
            msls_server.wikilink_graph.add_node(name)
            msls_server.wikilink_graph.add_edges_from([(name, e.link) for e in wikilinks])
        except Exception as e:
            log.error('Failed to extract wiklinks from %s'%file)
            log.error(e)
            continue

        # ls.show_message_log(f'{pathlib.Path(file).name} has {len(wikilinks)} links')
        percent = ifile*100.0/len(files)
        ls.progress.report(
            token,
            WorkDoneProgressReport(message=f'{name}', percentage = int(percent)),
        )
        await asyncio.sleep(0.1)
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


@msls_server.feature(
    DOCUMENT_LINK,
    DocumentLinkOptions(resolve_provider=True),
)
async def document_link(ls: MarkshiftLanguageServer, params: DocumentLinkParams):
    try:
        name = uri_to_link_name(params.text_document.uri)
        if not name in msls_server.wikilink_graph.nodes():
            log.warn('no such a page: %s'%params.text_document.uri)
            return None

        ret = []
        for l in msls_server.wikilink_graph.nodes[name]['wikilinks']:
            link = DocumentLink(
                range=Range(
                    start=Position(line=l['line']-1, character=l['column']-1),
                    end=Position(line=l['end_line']-1, character=l['end_column']),
                ),
                target=uris.from_fs_path(str(pathlib.Path(msls_server.lsp.workspace.root_path) / (l['link'] + file_ext))),
                tooltip="",
                data="",
            )
            ret.append(link)
        return ret
    except Exception as e:
        log.error("Error in Document Link:")
        log.error(str(e))
        return None

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

        ls.show_message(f'MarkshiftLanguageServer.exampleConfiguration value: {example_config}')

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


