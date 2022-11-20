# Markshift
This is an yet another markup language, <del>makeshift</del> markshift.

Please see this video: (TODO)

## Syntax
```txt
Hello world.
	create a list with a hard tab '\t'
		which can be nested
	the second element
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

Code highlight with highlight.js
	[@code python]
		import numpy as np
		print(np.sum(10))

Math with katex
	[@math]
		import numpy as np
		print(np.sum(10))
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
