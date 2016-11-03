#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys

header = r"""
<html>
<head>
<style>
table { border-collapse: collapse; }
table, tr, td, th { border: 1px solid #205c8f; }
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
        perfs[cur_day] += [(int(voie), color, grade, result)]
        continue

    r = r'\s*([a-z0-9]* \w\w\w)\w*: *(.*)'
    m = re.match(r, l)
    if m:
        date, comment = m.groups(1)
        cur_day = date
        days += [date]
        perfs[cur_day] = []
        continue

def fmt(result):
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
    print('<tr><td>' + g + '</td>')
    for d in days:
        s = '<td>'
        for voie, color, grade, result in perfs[d]:
            if grade == g:
                s += fmt(result)
        s += '</td>'
        print(s)
    print('</tr>')
print('</table>')

print('<p></p>')

print('<table><tr><th colspan="2">Location</th><th>Grade</th><th></th>')
aggregated = {}
for d in days:
    for voie, color, grade, result in perfs[d]:
        key = (voie, color, grade)
        if key in aggregated:
            aggregated[key] += fmt(result)
        else:
            aggregated[key] = fmt(result)
for g in reversed(sorted(grades)):
    for key, val in sorted(aggregated.items()):
        voie, color, grade = key
        if grade == g:
            print('<tr><td>' + str(voie) + '</td><td>' + color + '</td><td>' + g + '</td><td>' + val + '</td></tr')

print('</table>')

print(footer)

