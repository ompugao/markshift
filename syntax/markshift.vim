" originally taken from:
" https://github.com/syusui-s/scrapbox-vim/blob/master/syntax/scrapbox.vim

"  Original Copyright:
"  Scrapbox Syntax Plugin
"  Maintainer: Syusui Moyatani <syusui.s[a]gmail.com>
"  License: Creative Commons Zero 1.0 Universal
"  Version: 1.0.0

"syn match  markshiftDLink    /https\?:\/\/\S\{1,}/
syn match  markshiftTag      /#\S\{1,}/

""" Brackets
syn cluster markshiftSBracketContent contains=markshiftBig,markshiftItalic,markshiftStrike,markshiftUnder,markshiftBody
syn cluster markshiftSBracketLink    contains=markshiftSLink1,markshiftSLink2,markshiftSLink3
syn cluster markshiftSBracketImg    contains=markshiftSImg
syn region  markshiftSBracket        keepend start=/\[/ms=s+1 end=/\]/me=e-1 contains=@markshiftSBracketContent,@markshiftSBracketLink,markshiftPageLink oneline transparent
syn region  markshiftSLink           keepend start=/\[/ms=s+1 end=/\]/me=e-1 contains=@markshiftSBracketLink                                           oneline transparent contained

" [[markshift]]
syn match  markshiftStrong   /\[\[[^]]\{1,}\]\]/
" [markshift]
syn match  markshiftPageLink /.\{1,}/    contained
" [-*/_ markshift]
syn match  markshiftBody     /\s\{1,}.*/ contained contains=@markshiftSLink transparent
" [- markshift]
syn match  markshiftStrike   /-\{1,}.*/  contained contains=@markshiftSBracketContent,@markshiftSBracketLink
" [/ markshift]
syn match  markshiftItalic   /\/\{1,}.*/ contained contains=@markshiftSBracketContent,@markshiftSBracketLink
" [* markshift]
syn match  markshiftBig      /\*\{1,}.*/ contained contains=@markshiftSBracketContent,@markshiftSBracketLink
" [_ markshift]
syn match  markshiftUnder    /_\{1,}.*/  contained contains=@markshiftSBracketContent,@markshiftSBracketLink
" [$ markshift$]
syn match  markshiftInlineMath    /\$\{1,}.*\$/  contained contains=@markshiftSBracketContent,@markshiftSBracketLink

" [url]
syn match  markshiftSLink1   /\w\{1,}:\/\/\S\{1,}/              contained
" [url url_title]
syn match  markshiftSLink2   /\w\{1,}:\/\/\S\{1,}\s\{1,}.\{1,}/ contained
" [url_title url]
syn match  markshiftSLink3   /.\{1,}\s\{1,}\w\{1,}:\/\/\S\{1,}/ contained

" [@img markshift]
syn match  markshiftSImg    /@img\{1,}.*/  contained

""" Line Start
" > Scrpabox
" syn match  markshiftQuote    /^\s*>.*$/   contains=markshiftSBracket
" > 1. markshift
syn match  markshiftNumber   /^\s*\d\.\s/ contains=markshiftSBracket

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
hi def link markshiftSBracketLink   Underlined
hi def link markshiftSBracketImg Type
hi def link markshiftSLink1   Underlined
hi def link markshiftSLink2   Underlined
hi def link markshiftSLink3   Underlined
hi def link markshiftTag      Underlined
hi def link markshiftPageLink Structure
"hi def link markshiftDLink    Underlined
hi def link markshiftBig      Type
hi def link markshiftStrong   Type
hi def link markshiftItalic   Keyword
hi def link markshiftUnder    Underlined
hi def link markshiftInlineMath    Operator
hi def link markshiftNumber   Type
hi def link markshiftCode     String
hi def link markshiftQuote    SpecialComment
hi def link markshiftStrike   Comment
""hi markshiftStrike term=strikethrough gui=strikethrough
