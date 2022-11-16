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
	call lsp#register_notifications('msls', 
				\ function('s:notification_cb'))
endfunction

function! s:notification_cb(server, data) abort
	let l:res = get(a:data, 'response', {})
	if has_key(l:res, 'method') && l:res['method'] == 'window/showDocument'
		execute ':e ' . lsp#utils#uri_to_path(l:res['params']['uri'])
		call lsp#client#send_response(lsp#get_server_info('msls')['lsp_id'],
			{'result': {'success': v:true}})
	endif
endfunction

augroup vim_lsp_settings_markshift-language-server
  au!
  au User lsp_setup call s:setup_markshift()
augroup END

