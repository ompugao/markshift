import markshift.parser
import markshift.htmlrenderer
renderer = markshift.htmlrenderer.HtmlRenderer()
parser = markshift.parser.Parser(renderer)
with open('sample/input.ms', 'r') as f:
    tree = parser.parse([l.rstrip('\n') for l in f.readlines()])
    # tree = parser.parse(filter(lambda l: len(l) > 0, [l.rstrip() for l in f.readlines()]))
# from IPython.terminal import embed; ipshell=embed.InteractiveShellEmbed(config=embed.load_default_config())(local_ns=locals())

with open('sample/output.html', 'w') as f:
    f.write(tree.render())
