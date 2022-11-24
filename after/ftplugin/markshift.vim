function! s:_execute_command(command_name) abort
	if lsp#get_server_status('msls') !=# 'running'
		return
	endif
	let params = {}
	let params['command_name'] = a:command_name
	let params['server_name'] = 'msls'
	call lsp#ui#vim#execute_command#_execute(params)
endfunction

function! s:show_previewer() abort
	call s:_execute_command('showPreviewer')
endfunction

function! s:hide_previewer() abort
	call s:_execute_command('hidePreviewer')
endfunction

setlocal suffixesadd=.ms
nnoremap <silent> gf :call markshift#open_wikilink(expand('<cfile>'))<CR>
vnoremap <silent> gf :call markshift#open_wikilink(expand(@*))<CR>

nnoremap <buffer><silent> <Plug>(markshift-previewer-show) :<C-u>call <SID>show_previewer()<CR>
nnoremap <buffer><silent> <Plug>(markshift-previewer-hide) :<C-u>call <SID>hide_previewer()<CR>
command! MarkshiftHidePreviewer call s:hide_previewer()
command! MarkshiftShowPreviewer call s:show_previewer()

if get(g:, 'markshift_enable_default_mappings', 0)
	nnoremap <buffer> <F8> <cmd>MarkshiftHidePreviewer<CR>
	nnoremap <buffer> <F9> <cmd>MarkshiftShowPreviewer<CR>
endif

augroup Markshift
    au!
    autocmd BufWinEnter *.ms call markshift#preview_buffer(bufnr('%'))
augroup END

