# -*- coding: utf-8 -*-

from contextlib import ExitStack, closing
import functools
import json
import logging
import tempfile
import pathlib
import shutil
import sqlite3

log = logging.getLogger(__name__)

@functools.lru_cache(maxsize=3)
def zotero_comp(ls, zotero_path = '~/Zotero'):
    path = (pathlib.Path(zotero_path) / ('zotero.sqlite')).expanduser()
    if not path.exists():
        return []

    with ExitStack() as stack:
        dir = stack.enter_context(tempfile.TemporaryDirectory())
        path_copied = pathlib.Path(dir) / 'zotero.db.msls'
        shutil.copy(path, path_copied)

        conn = stack.enter_context(closing(sqlite3.connect(path_copied)))
        cur = stack.enter_context(conn)
        try:
            cachedata = cur.execute("SELECT data from syncCache").fetchall()
        except sqlite3.OperationalError as e:
            mes = 'Zotero database cannot be accessed : %s'%str(e)
            log.error(mes)
            ls.show_message(mes)
            return []
        jsdata = [json.loads(d[0]) for d in cachedata]
        papers = []
        for d in jsdata:
            if ('itemType' in d['data'].keys()):
                if d['data']['itemType'] in ['conferencePaper', 'journalArticle', 'preprint', 'thesis']:
                    papers.append(d)
        compitems = [(p['data']['title'], p['data']['title'] + ' zotero://select/library/items/' + p['key']) for p in papers]
    return compitems
