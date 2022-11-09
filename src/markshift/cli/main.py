#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.abspath(''))
import click
import re

import markshift.parser
import markshift.htmlrenderer

@click.command()
@click.argument('inputfile', type=click.Path(exists=True))
@click.argument('outputfile', type=click.Path(exists=False))
def main(inputfile, outputfile):
    renderer = markshift.htmlrenderer.HtmlRenderer()
    parser = markshift.parser.Parser(renderer, use_tokenizer=True)
    template = """
    <!DOCTYPE html>
    <head>
    <!-- highlight.js -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.6.0/styles/github.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.6.0/highlight.min.js"></script>
    <script>hljs.highlightAll();</script>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/github-markdown.min.css"/>

    <!-- katex -->
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
    .image {
        vertical-align: top; 
    }
    </style>
    </head>
    <body>
    %%BODY%%
    </body>
    </html>
    """   
    with open(click.format_filename(inputfile), 'r') as f:
        tree = parser.parse([l.rstrip('\n') for l in f.readlines()])

    with open(outputfile, 'w') as f:
        f.write(template.replace('%%BODY%%', tree.render()))


if __name__ == '__main__':
    main()
