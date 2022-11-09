Hello world:
	This format is indentation-based.
	We can write [* bold] text.
	of course, [/ italic] as well.
		multiple indentation is available.
	inline math:
		you can write a math [$ O(n)$] [$ O^2(n)$] inline.
	[/* bold italic symbols]

code embeddng (powered by highlight.js):
	[@code python]
		import numpy as np
		def print_func(arg):
			print(arg)
		print_func('hoge')
		print(np.zeros(4))


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

