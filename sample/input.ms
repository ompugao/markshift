[@h1 A title of sample text]
This is the sample file for markshift.

[@h2 section]
an example of table syntax:
	[@table]
		hoge	fuga	piyo
		ぽん	ぴよ	ぴ
		[google https://google.com]	[meta https://facebook.com]	[apple https://apple.com]

Texts are organized with 'tab'.
	Indent your text with 'tab' to create a list.
		which can be nested.
	We can write [* bold] text.
	of course, [/ italic] as well.
	[/* bold italic text]
	here is [- deleted text]
	this is a text with [_ underline]
	inline math:
		you can write a math [$ O(n)$] inline, like this [$ O(n^2)$].
	[/* bold italic symbols]
	invalid text will be shown as it is. [*
	inline code: [`  hogehoge[]]   `]
	[local link]

Links:
	you can embed images: [@img https://via.placeholder.com/50 width=300].
	you can set alt text: [@img https://via.placeholder.com/50 "this is an alt text"].
		like this as well: [@img "this is also an alt text" https://via.placeholder.com/50].
		[@img https://via.placeholder.com/50 width=300]
	url: [google https://google.com]
	url2: [https://google.com google]
	url3: [https://google.co.jp/]
	url4: [g o o g l e https://google.co.jp/]
	url5: [https://google.co.jp/ g o o g l e]
	url6: [https://google.co.jp/ https://google.co.jp/]

code embeddng (powered by highlight.js):
sample python code:
[@code python]
	import numpy as np
	def print_func(arg):
		print(arg)
	print_func('hoge')
	print(np.zeros(4))
sample c++ code:
[@code cpp]
	#include <iostream>
	#include <vector>
	#include <string>
	
	int main(int argc, char * argv[])
	{
		std:cout << 1+2+3 << std::endl;
		return 0;
	}


math embedding (powered by katex):
	[@math]
		s = sum_{i=0}^{10} {a_i}

quote blocks:
	[@quote]
		hoge
		[* bold quote]
		piyo
	[@quote]
		new quote
		bra bra brah

vim: set fileencoding=utf-8 ft=markshift:
