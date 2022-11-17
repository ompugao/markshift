import glob
import re

regexp = re.compile('(.*)\[\[(.*)\]\](.*)')
regexp_asset = re.compile('(.*)\.\./assets(.*)')
for file in glob.glob('**/*.ms'):
    lines = []
    with open(file) as f:
        while line := f.readline():
            if line.startswith('\t'):
                line = line[1:]

            m = regexp.match(line)
            while m is not None:
                line = m.group(1) + '[' + m.group(2) + ']' + m.group(3)
                m = regexp.match(line)
            line = re.sub('\.\./assets', 'assets', line)
            lines.append(line)

    with open(file, 'w') as f:
        f.write(''.join(lines))
