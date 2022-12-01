" originally taken from:
" https://github.com/syusui-s/scrapbox-vim/blob/master/syntax/scrapbox.vim

"  Original Copyright:
"  Scrapbox Syntax Plugin
"  Maintainer: Syusui Moyatani <syusui.s[a]gmail.com>
"  License: Creative Commons Zero 1.0 Universal
"  Version: 1.0.0

syn match  markshiftTag      /#\S\{1,}/

""" Brackets
syn cluster markshiftSBracketContent contains=markshiftBig,markshiftItalic,markshiftStrike,markshiftUnder,markshiftBody,markshiftInlineMath
syn cluster markshiftSBracketLink    contains=markshiftSLink1,markshiftSLink2,markshiftSLink3
syn region  markshiftSBracket        keepend start=/\[/ms=s+1 end=/\]/me=e-1 contains=@markshiftSBracketContent,@markshiftSBracketLink,markshiftPageLink oneline transparent

" [[markshift]]
syn match  markshiftStrong   /\[\[[^]]\{1,}\]\]/
" [markshift]
syn match  markshiftPageLink /[^\]]\{1,}/    contained
" [-*/_ markshift]
syn match  markshiftBody     /\s\{1,}.*/ contained contains=@markshiftSLink transparent
" [- markshift]
syn match  markshiftStrike   /-\{1,}.*/  contained contains=@markshiftSBracketContent
" [/ markshift]
syn match  markshiftItalic   /\/\{1,}.*/ contained contains=@markshiftSBracketContent
" [* markshift]
syn match  markshiftBig      /\*\{1,}.*/ contained contains=@markshiftSBracketContent
" [_ markshift]
syn match  markshiftUnder    /_\{1,}.*/  contained contains=@markshiftSBracketContent

" [$ markshift$]
syn include @tex syntax/tex.vim
syn region markshiftInlineMath start="\\\@<!\$" end="\$" skip="\\\$" contains=@tex keepend

" [url]
let b:url_regex = '\w\{1,}:\/\/\S\{1,}'
"syn match  markshiftSLink1   /\w\{1,}:\/\/\S\{1,}/              contained
execute 'syn match  markshiftSLink1  /' . url_regex . '/        contained'
" [url url_title]
"syn match  markshiftSLink2   /\zs\s*\w\{1,}:\/\/\S\{1,}\ze\s\{1,}.\{1,}/ contained conceal cchar=🔗
execute 'syn match  markshiftSLink2  /\zs\s*' . url_regex . '\ze\s\{1,}.\{1,}/ contained conceal cchar=🔗'
" [url_title url]
"syn match  markshiftSLink3   /.\{1,}\s\{1,}\zs\w\{1,}:\/\/\S\{1,}\ze/ contained conceal cchar=🔗
execute 'syn match  markshiftSLink3   /.\{1,}\s\{1,}\zs' . url_regex . '\ze/ contained conceal cchar=🔗'

" [@img markshift]
syn match  markshiftSImg    /\[\zs@img\s\{1,}.*\ze\]/

""" Code
" [`"markshift"`]
syn region markshiftCode     start=/\[`/ end=/`\]/ skip=/\\`/ oneline
" $ ./markshift.sh or % ./markshift.sh
"syn region markshiftCode     start=/^\s*\$/ start=/^\s*%/ end=/$/
" [@code lang]
syn region markshiftCode     start=/^\z(\s*\)\[@code \(\S\+\)\]/ skip=/^\z1\s/ end=/^/
" [@math lang]
syn region markshiftCode     start=/^\z(\s*\)\[@math \(\S\+\)\]/ skip=/^\z1\s/ end=/^/
" [@math quote]
syn region markshiftQuote     start=/^\z(\s*\)\[@quote \(\S\+\)\]/ skip=/^\z1\s/ end=/^/

""" Highlight

hi def link markshiftTitle    Function
hi def link markshiftPageLink Structure
hi def link markshiftContainsURL Underlined
hi def link markshiftSImg Type
"hi def link markshiftSLink1   Underlined
"hi def link markshiftSLink2   Underlined
"hi def link markshiftSLink3   Underlined
"hi def link markshiftTag      Underlined
hi def link markshiftBig      Type
hi def link markshiftStrong   Type
hi def link markshiftItalic   Keyword
hi def link markshiftUnder    Underlined
hi def link markshiftInlineMath    Operator
hi def link markshiftNumber   Type
hi def link markshiftCode     String
hi def link markshiftQuote    SpecialComment
hi def link markshiftStrike   Comment
hi def link markshiftSB Include
