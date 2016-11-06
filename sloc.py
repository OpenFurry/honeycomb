from collections import OrderedDict
import sys


total = 0
files = OrderedDict()
for arg in sys.argv[1:]:
    files[arg] = 0
    with open(arg, 'r') as f:
        for l in f:
            line = l.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            files[arg] += 1
    total += files[arg]

print('Count\tLocation')
for f, c in files.items():
    print('{0:5d}\t{1}'.format(c, f))
print('{0:5d}\tTOTAL'.format(total))
