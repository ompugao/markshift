# -*- coding: utf-8 -*-

import sqlite3
import json
import pathlib
import functools
import logging

log = logging.getLogger(__name__)

@functools.lru_cache(maxsize=3)
def zotero_comp(ls, zotero_path = '~/Zotero'):
    path = (pathlib.Path(zotero_path) / ('zotero.sqlite')).expanduser()
    if not path.exists():
        return []
    conn = sqlite3.connect(path)
    cur = conn.cursor()
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
    cur.close()
    conn.close()
    return compitems
