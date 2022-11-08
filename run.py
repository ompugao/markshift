import markshift
import markshift.htmlrenderer
renderer = markshift.htmlrenderer.HtmlRenderer()
parser = markshift.Parser(renderer)
with open('sample/input.ms', 'r') as f:
    tree = parser.parse([l.rstrip('\n') for l in f.readlines()])
    # tree = parser.parse(filter(lambda l: len(l) > 0, [l.rstrip() for l in f.readlines()]))
# from IPython.terminal import embed; ipshell=embed.InteractiveShellEmbed(config=embed.load_default_config())(local_ns=locals())

with open('sample/output.html', 'w') as f:
    f.write("""
            <!DOCTYPE html>
            <head>
            <link rel="stylesheet" href="../highlightjs/styles/github.min.css">
            <script src="../highlightjs/highlight.min.js"></script>
            <script>hljs.highlightAll();</script>

            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.3/dist/katex.min.css" integrity="sha384-Juol1FqnotbkyZUT5Z7gUPjQ9gzlwCENvUZTpQBAPxtusdwFLRy382PSDx5UUJ4/" crossorigin="anonymous">
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.3/dist/katex.min.js" integrity="sha384-97gW6UIJxnlKemYavrqDHSX3SiygeOwIZhwyOKRfSaf0JWKRVj9hLASHgFTzT+0O" crossorigin="anonymous"></script>
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.3/dist/contrib/auto-render.min.js" integrity="sha384-+VBxd3r6XgURycqtZ117nYw44OOcIax56Z4dCRWbxyPt0Koah1uHoK0o4+/RRE05" crossorigin="anonymous"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    renderMathInElement(document.body, {
                      // customised options
                      // • auto-render specific keys, e.g.:
                      delimiters: [
                          {left: '$$', right: '$$', display: false},
                          {left: '$', right: '$', display: false},
                          {left: '\\[\\[', right: '\\]\\]', display: true}
                      ],
                      // • rendering keys, e.g.:
                      throwOnError : false
                    });
                });
            </script>
            <style>
            .empty-line{
                list-style-type: none;
            }
            </style>
            </head>
            <body>
            """)
    f.write(tree.render())
    f.write("</body>")

"""
            <link rel="stylesheet"
                  href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.6.0/styles/default.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.6.0/highlight.min.js"></script>
"""
