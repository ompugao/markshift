
function! s:_execute_command(command_name) abort
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

function! s:_preview_focused_buffer(buf) abort
	let l:path = lsp#utils#get_buffer_uri(a:buf)
	let params = {}
	let params['bufnr'] = a:buf
	let params['server_name'] = 'msls'
	let params['command_name'] = 'forceRedraw'
	let params['command_args'] = {}
	let params['command_args']['buffer_uri'] = l:path
	call lsp#ui#vim#execute_command#_execute(params)
endfunction

" We need a definition guard because we invoke 'edit' which will reload this
" script while this function is running. We must not replace it.
if !exists('*s:_open_ms_file')
	function! s:_open_ms_file(filename) abort
		let l:file = substitute(a:filename, '^\(.*\)\.ms$', '\1', '')
		if l:file == ''
			return
		endif
		execute ':e ' . l:file . '.ms'
	endfunction
endif

command! MarkshiftShowPreviewer call s:show_previewer()
command! MarkshiftHidePreviewer call s:hide_previewer()

setlocal suffixesadd=.ms
nnoremap <silent> gf :call <SID>_open_ms_file(expand('<cfile>'))<CR>
vnoremap <silent> gf :call <SID>_open_ms_file(expand(@*))<CR>

augroup Markshift
    au!
    autocmd CursorMoved * call s:_preview_focused_buffer(bufnr('%'))
augroup END

