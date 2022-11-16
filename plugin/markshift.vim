if exists('g:loaded_markshift')
  finish
endif
let g:loaded_markshift = 1

function! s:setup_markshift() abort
	if get(s:, 'setup') | return | endif
	let s:setup = 1
	let s:cliend_id = lsp#register_server({
				\ 'name': 'msls',
				\ 'cmd': ['python3', '-m', 'markshift.langserver.server'],
				\ 'allowlist': ['markshift'],
				\ })
endfunction

augroup vim_lsp_settings_markshift-language-server
  au!
  au User lsp_setup call s:setup_markshift()
augroup END

