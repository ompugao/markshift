if exists('g:loaded_markshift')
  finish
endif
let g:loaded_markshift = 1

let g:markshift_concatview_cmd =  get(g:, 'markshift_concatview_cmd', ':edit')

command! -nargs=+ -complete=file MarkshiftCat call markshift#concat_view(<q-args>) 

augroup markshift-filetype
  au!
  au BufNewFile,BufRead *.ms set filetype=markshift
augroup END

