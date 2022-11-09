Hello world:
	This format is indentation-based.
	We can write [* bold] text.
	of course, [/ italic] as well.
		multiple indentation is available.
	inline math:
		you can write a math [$ O(n)$] -- [$ O^2(n)$] inline.
	[/* bold italic symbols]
	inline code: [`  hogehoge[]]   `]

Links:
	you can embed images: [@img https://via.placeholder.com/50].
	you can set alt text: [@img https://via.placeholder.com/50 "this is an alt text"].
		like this as well: [@img "this is also an alt text" https://via.placeholder.com/50].
		[@img https://via.placeholder.com/50]
	url: [google https://google.com]
	url2: [https://google.com google]
	url3: [https://google.co.jp/]


code embeddng (powered by highlight.js):
	[@code python]
		import numpy as np
		def print_func(arg):
			print(arg)
		print_func('hoge')
		print(np.zeros(4))
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

