if exists('g:loaded_markshift')
  finish
endif
let g:loaded_markshift = 1

augroup markshift-filetype
  au!
  au BufNewFile,BufRead *.ms set filetype=markshift
augroup END

command! MarkshiftCatAll :term bash -c "ls -1 *.ms | xargs -I{} sh -c \"echo {}; echo '----------------'; cat {}; echo '----------------'\""<CR>
