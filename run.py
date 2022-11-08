import markshift.parser
import markshift.htmlrenderer
renderer = markshift.htmlrenderer.HtmlRenderer()
parser = markshift.parser.Parser(renderer)
with open('sample/input.ms', 'r') as f:
    tree = parser.parse(f.readlines())
with open('sample/output.html', 'w') as f:
    f.write(tree.render())
