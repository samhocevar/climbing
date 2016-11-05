#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys

header = r"""
<html>
<head>
<style>
body { font-family: sans-serif; }
table { border-collapse: collapse; }
table, tr, td, th {
    border: 1px solid #205c8f;
}
td {
    font-size: 0.9em;
}
th {
    background-color: #205C8F;
    color: white;
}
</style>
</head>
<body>
"""

footer = r"""
</body>
</html>
"""

grades = {}
days = []
perfs = {}
cur_day = None

for l in sys.stdin.readlines():
    l = l.strip()
    if not l:
        continue

    r = r'\s*(\d*)\s*(\w*)\s*([+/0-9a-z]*)\s*(OK|--)\s*(.*)'
    m = re.match(r, l)
    if m:
        voie, color, grade, result, comm = m.groups(1)
        grades[grade] = True
        perfs[cur_day] += [(int(voie), color, grade, result, comm)]
        continue

    r = r'\s*([a-z0-9]* \w\w\w)\w*: *(.*)'
    m = re.match(r, l)
    if m:
        date, comment = m.groups(1)
        cur_day = date
        days += [date]
        perfs[cur_day] = []
        continue

def gr2str(grade):
    lut = { '4':      '#5189f1',
            '4+':     '#3169e1',
            '4b':     '#3169e1',
            '5a':     '#a0eea0',
            '5a+':    '#80de80',
            '5b':     '#60ce60',
            '5b+':    '#40be40',
            '5b+/c':  '#30b630',
            '5c':     '#20ae20',
            '5c+':    '#009e00',
            '5c+/6a': '#008e00',
            '6a':     '#eeeea0',
            '6a+':    '#dede80',
            '6b':     '#cece60',
            '6b+':    '#bebe40',
            '6c':     '#aeae20',
            '6c+':    '#9e9e00', # LOL
          }
    c = lut[grade] if grade in lut else 'white'
    return '<td style="background: ' + c + '">' + grade + '</td>'

def res2str(result):
    if result == 'OK':
        return '<span style="color:#30aa30">✔</span>'
    else:
        #return '<span style="color:red">✗</span>'
        return '<span style="color:red">×</span>'

print(header)

print('<table><tr><th>Grade</th>')
for d in days:
    print('<th>' + d + '</th>')
print('</tr>')

for g in reversed(sorted(grades)):
    print('<tr>' + gr2str(g))
    for d in days:
        s = '<td>'
        for voie, color, grade, result, comm in perfs[d]:
            if grade == g:
                s += res2str(result)
        s += '</td>'
        print(s)
    print('</tr>')
print('</table>')

print('<p></p>')

print('<table><tr><th>Route</th><th>Grade</th><th></th><th>Comments</th>')
aggregated = {}
comments = {}
for d in days:
    for voie, color, grade, result, comm in perfs[d]:
        key = (voie, color, grade)
        aggregated[key] = ''
        comments[key] = ''
for d in days:
    for voie, color, grade, result, comm in perfs[d]:
        key = (voie, color, grade)
        aggregated[key] += res2str(result)
        if comm:
            if comments[key]:
                comments[key] += ' — '
            comments[key] += d + ': ' + comm
for g in reversed(sorted(grades)):
    for key, val in sorted(aggregated.items()):
        voie, color, grade = key
        if grade != g:
            continue
        print('<tr><td>' + str(voie) + ' ' + color + '</td>' + gr2str(g) + '<td>' + val + '</td><td>' + comments[key] + '</td></tr>')

print('</table>')

print(footer)

