" originally taken from:
" https://github.com/syusui-s/scrapbox-vim/blob/master/syntax/scrapbox.vim

"  Original Copyright:
"  Scrapbox Syntax Plugin
"  Maintainer: Syusui Moyatani <syusui.s[a]gmail.com>
"  License: Creative Commons Zero 1.0 Universal
"  Version: 1.0.0

syn clear

""" Brackets
syn cluster markshiftSBracketContent contains=markshiftBig,markshiftItalic,markshiftStrike,markshiftUnder,markshiftBody,markshiftInlineMath
syn cluster markshiftSBracketLink    contains=markshiftSLink1,markshiftSLink2,markshiftSLink3

" syn region markshiftBracket0           matchgroup=hlLevel0 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket1
" syn region markshiftBracket1 contained matchgroup=hlLevel1 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket2
" syn region markshiftBracket2 contained matchgroup=hlLevel2 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket3
" syn region markshiftBracket3 contained matchgroup=hlLevel3 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket4
" syn region markshiftBracket4 contained matchgroup=hlLevel4 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket5
" syn region markshiftBracket5 contained matchgroup=hlLevel5 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket6
" syn region markshiftBracket6 contained matchgroup=hlLevel6 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket7
" syn region markshiftBracket7 contained matchgroup=hlLevel7 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket8
" syn region markshiftBracket8 contained matchgroup=hlLevel8 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket9
" syn region markshiftBracket9 contained matchgroup=hlLevel9 start="\[" end="\]" skip="|.\{-}|" contains=@markshiftSBracketLink,markshiftBracket0

"syn region  markshiftSLink        keepend start=/\[/ms=s+1 end=/\]/me=e-1 contains=@markshiftSBracketLink oneline transparent contained
syn region  markshiftSBracket        keepend start=/\[/ms=s+1 end=/\]/me=e-1 contains=@markshiftSBracketLink oneline
syn match markshiftSBracketNoURL /\[\(.\+:\/\/\\*\)\@!.\{-}\]/ms=s+1,me=e-1 keepend contains=@markshiftSBracketContent,markshiftPageLink

" [markshift]
" do not match url!
" exe 'syn match  markshiftPageLink /\(.\{1,}:\/\/\S\{1,}\)\@!.\+/    contained'
" exe 'syn match markshiftPageLink /\(.\{1,}:\/\/.\*\)\@!.\{-}/ contained'
"syn match markshiftPageLink /^\(\(.\+:\/\/\\*\)\@!.\*\)$/ contained
"syn match markshiftPageLink /.\+/ contained
syn match markshiftPageLink /[^\[\]]\+/ contained  " not sure why I need to exlude '['

" [-*/_ markshift]
syn match  markshiftBody     /\s\{1,}[^\[\]]\+/ contained contains=@markshiftSBracket transparent
"syn match  markshiftBody     /\s\{1,}.\+/ contained contains=@markshiftBracket0,@markshiftBracket1,@markshiftBracket2,@markshiftBracket3,@markshiftBracket4,@markshiftBracket5,@markshiftBracket6,@markshiftBracket7,@markshiftBracket8,@markshiftBracket9 transparent
" [- markshift]
syn match  markshiftStrike   /-\{1,}[^\[\]]\+/  contained contains=@markshiftSBracketContent
" [/ markshift]
syn match  markshiftItalic   /\/\{1,}[^\[\]]\+/ contained contains=@markshiftSBracketContent
" [* markshift]
syn match  markshiftBig      /\*\{1,}[^\[\]]\+/ contained contains=@markshiftSBracketContent
" [_ markshift]
syn match  markshiftUnder    /_\{1,}[^\[\]]\+/  contained contains=@markshiftSBracketContent

" [$ markshift$]
syn include @tex syntax/tex.vim
syn region markshiftInlineMath start="\\\@<!\$" end="\$" skip="\\\$" contained contains=@tex keepend

" [url]
let url_regex = '\w\{1,}:\/\/\S\{1,}'
execute 'syn match  markshiftSLink1  /\zs' . url_regex . '\ze/        contained'
" [url url_title]
execute 'syn match  markshiftSLink2  /\zs\s*' . url_regex . '\s\{1,}\ze.\{1,}/ contained conceal cchar=🔗'
" [url_title url]
execute 'syn match  markshiftSLink3   /.\{1,}\zs\s\{1,}' . url_regex . '\ze/ contained conceal cchar=🔗'

" [@img markshift]
syn match  markshiftSImg    /\[\zs@img\s\{1,}.*\ze\]/

" {@line_property ...}
syn region markshiftLineProperty   start=/{@\w\+/ end=/}/ oneline
" #line_anchor
syn match  markshiftLineAnchor   /.*\s\+\zs\#\S\+\ze$/
"syn match  markshiftTag      /#\S\{1,}/
" some task {@task status=done}
syn match  markshiftTaskHighPriority     /^\s*\zs.*{@task.*priority=high.*}.*$/
syn match  markshiftTaskDone     /^\s*\zs.*{@task.*status=done.*}.*$/

""" Code
" [`"markshift"`]
syn region markshiftInlineCode     start=/\[`/ end=/`\]/ skip=/\\`/ oneline
" $ ./markshift.sh or % ./markshift.sh
"syn region markshiftCode     start=/^\s*\$/ start=/^\s*%/ end=/$/
" [@code lang]
syn region markshiftCode start=/^\z(\s*\)\[@code \(\S\+\)\]/ skip=/^\(\z1\s\|\n\+\z1\)/ end=/^/
" [@math]
syn region markshiftMath     matchgroup=texDelimiter start=/^\z(\s*\)\[@math\]/ skip=/^\(\z1\s\|\n\+\z1\)/ end=/^/ contains=@texMathZoneGroup keepend
" [@quote]
syn region markshiftQuote     start=/^\z(\s*\)\[@quote\]/ skip=/^\(\z1\s\|\n\+\z1\)/ end=/^/

""" Highlight

hi def link markshiftTitle    Function
hi def link markshiftPageLink Structure
hi def link markshiftSImg Type
hi def link markshiftSBracket Operator
hi def link markshiftSLink1   Operator
hi def link markshiftSLink2   Operator
hi def link markshiftSLink3   Operator
"hi def link markshiftTag      Underlined
hi def link markshiftBig      Type
hi def link markshiftItalic   Keyword
hi def link markshiftUnder    Underlined
hi def link markshiftInlineMath    Operator
hi def link markshiftNumber   Type
hi def link markshiftInlineCode     String
hi def link markshiftLineProperty  Comment
hi def link markshiftLineAnchor Keyword
hi def link markshiftCode     String
"hi def link markshiftMath     Operator
hi def link markshiftQuote    SpecialComment
hi def link markshiftStrike   Comment
hi def link markshiftTaskHighPriority Type
hi def link markshiftTaskDone NonText
hi Folded ctermbg=Black ctermfg=Yellow

hi def hlLevel0 ctermfg=red		guifg=red1
hi def hlLevel1 ctermfg=yellow	guifg=orange1
hi def hlLevel2 ctermfg=green	guifg=yellow1
hi def hlLevel3 ctermfg=cyan	guifg=greenyellow
hi def hlLevel4 ctermfg=magenta	guifg=green1
hi def hlLevel5 ctermfg=red		guifg=springgreen1
hi def hlLevel6 ctermfg=yellow	guifg=cyan1
hi def hlLevel7 ctermfg=green	guifg=slateblue1
hi def hlLevel8 ctermfg=cyan	guifg=magenta1
hi def hlLevel9 ctermfg=magenta	guifg=purple1

