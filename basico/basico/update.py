#!/usr/bin/env python3
import json

# read all keywords
with open('./keywords.txt', 'r') as fk:
    keywords = []
    for line in fk.readlines():
        line = line.strip()
        keywords += [kw for kw in line.split(' ') if len(kw)]
# read origin syntax.json
with open('./syntax.json', 'r') as fs:
    syntax = json.load(fs)
match = r'\|\b({kw})\b'.format(kw='|'.join(keywords))
patterns = syntax['repository']['keywords']['patterns']
for pattern in patterns:
    if pattern['name'] == 'keyword.control.basico':
        pattern['match'] = match
# patch syntax.json
with open('./syntax.json', 'w') as fs:
    json.dump(syntax, fs, indent='\t')
print('OK')
