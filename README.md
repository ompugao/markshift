# Markshift
This is an yet another markup language, <del>makeshift</del> markshift.

Please see this video:
[![youtube video](https://img.youtube.com/vi/GX7vkJTXu2U/0.jpg)](https://www.youtube.com/watch?v=GX7vkJTXu2U)

## Features
- Simple markup syntax with `\t` and `[]`
    - heavily inspired by [Scrapbox](https://scrapbox.io)
- Zettelkasten (dynamic wiki links) first, powered by Markshift Language Server.
- Vim plugin included.
- Zotero integration.

## Syntax
```txt
Hello world.
	create a list with a hard tab `\t'
		which can be nested
	the second element
	the third element
	[@quote]
		quoted text must be indented with '\t'

Decoration:
	[* bold text]
	[/ italic text]
	[*/ bold italic text]

Links:
	[wikilink]
	[https://google.com url title]
	[url title https://google.com]
	[@img https://via.placeholder.com/50 width=300 height=300]

Code highlight with highlight.js
	[@code python]
		import numpy as np
		print(np.sum(10))
	[` inline code `]

Math with katex
	[@math]
		O(n^2)\\
		sum_{i=0}^{10}{i} = 55
	inline math: [$ O(n log(n)) $]
```

## Zettelkasten with Markshift Language Server (msls)
- Setup Markshift Language Server (msls) with your client
```vim
function! s:setup_markshift() abort
	let s:msls_client_id = lsp#register_server({
        \ 'name': 'msls',
        \ 'cmd': ['msls', '--never_steal_focus', '--always_on_top', '--zotero_path=~/Zotero'],
        \ 'allowlist': ['markshift'],
        \ })
        "or:
        "\ 'cmd': ['python3', '-m', 'markshift.langserver.server'],
endfunction

augroup vim-lsp-msls
  au!
  au User lsp_setup call s:setup_markshift()
augroup END
```
