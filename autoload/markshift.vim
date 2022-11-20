
let s:file_ext = '.ms'

" We need a definition guard because we invoke 'edit' which will reload this
" script while this function is running. We must not replace it.
"if !exists('*s:_open_ms_file')
function! s:_open_ms_file(filename) abort
	let l:file = substitute(a:filename, '^\(.*\)\' . s:file_ext . '$', '\1', '')
	if l:file == ''
		return
	endif
	execute ':e ' . l:file . s:file_ext
endfunction
"endif

function! markshift#open_wikilink(filename) abort
	call s:_open_ms_file(a:filename)
endfunction

let s:bufname = 'markshift-concatview'

let s:ms_last_file = ''
function! s:_preview_buffer(buf) abort
	if lsp#get_server_status('msls') !=# 'running'
		return
	endif
	let l:path = lsp#utils#get_buffer_uri(a:buf)
	if s:ms_last_file == l:path
		return
	endif
	let s:ms_last_file = l:path
	let params = {}
	let params['bufnr'] = a:buf
	let params['server_name'] = 'msls'
	let params['command_name'] = 'forceRedraw'
	let params['command_args'] = {}
	let params['command_args']['buffer_uri'] = l:path
	call lsp#ui#vim#execute_command#_execute(params)
endfunction


"if !exists('*s:_openwindow')
function! s:_openwindow()
	if bufwinnr(s:bufname) == -1
		execute g:markshift_concatview_cmd . ' ' . s:bufname
		"setlocal nobuflisted
		setlocal buftype=nofile noswapfile
		"setlocal bufhidden=delete
		setlocal nonumber
		setlocal norelativenumber
		setlocal filetype=markshift
		execute "augroup MarkshiftConcatView"
		execute "autocmd!"
		execute "autocmd BufEnter " . s:bufname . " map <buffer> q <C-w>c<CR>"
		execute "autocmd CursorMoved " . s:bufname " call s:_preview_buffer(bufnr('%'))"
		execute "augroup END"
	endif
	execute bufwinnr(s:bufname) . 'wincmd w'
endfunction
"endif

function! markshift#preview_buffer(bnr) abort
	call s:_preview_buffer(a:bnr)
endfunction

function! s:truncate(str, width) abort
  " Original function is from mattn.
  " http://github.com/mattn/googlereader-vim/tree/master

  if a:str =~# '^[\x00-\x7f]*$'
    return len(a:str) < a:width
          \ ? printf('%-' . a:width . 's', a:str)
          \ : strpart(a:str, 0, a:width)
  endif

  let ret = a:str
  let width = strwidth(a:str)
  if width > a:width
    let ret = s:strwidthpart(ret, a:width)
    let width = strwidth(ret)
  endif

  if width < a:width
    let ret .= repeat(' ', a:width - width)
  endif

  return ret
endfunction

function! s:remove_suffix(str, suffix) abort
  let idx = strridx(a:str, a:suffix)
  if idx < 0
    return a:str
  endif
  return s:truncate(a:str, idx)
endfunction

"if !exists('*s:_concat_view')
function! s:_concat_view(argstr) abort
	"let l:files = a:000
	let l:files = split(a:argstr, '\\\@<!\s')
	echo l:files
	call s:_openwindow()
	setlocal modifiable noreadonly
	" erase all existing lines
	silent! file `=bufname`
	execute ":1,$d"
	" write all files
	for l:file in l:files
		call append(line('$'), '-------- [' . s:remove_suffix(l:file, s:file_ext) . ']  --------')
		call cursor(line('$'), 0)
		execute ':r ' . l:file
		call append(line('$'), '')
		call cursor(line('$'), 0)
	endfor
	call deletebufline(bufnr(s:bufname), 1)
	setlocal nomodifiable readonly
endfunction
"endif
function! markshift#concat_view(argstr) abort
	call s:_concat_view(a:argstr)
endfunction

