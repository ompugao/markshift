
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

command! MarkshiftShowPreviewer call s:show_previewer()
command! MarkshiftHidePreviewer call s:hide_previewer()

augroup Markshift
    " autocmd BufWinEnter,BufWritePost <buffer> call s:MarkdownSetupFolding()
    " autocmd InsertEnter,InsertLeave <buffer> call s:MarkdownSetupFolding()
    " autocmd CursorHold,CursorHoldI <buffer> call s:MarkdownSetupFolding()
augroup END

