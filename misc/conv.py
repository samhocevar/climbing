#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, math

# How much previous days count
DECAY = 1.5

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
<div style="float:right">
  <a href="jo.html">jo</a> |
  <a href="jy.html">jy</a> |
  <a href="s.html">s</a>
</div>
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

def hist2str(history):
    history = [0] + history
    ret = '<span style="display:block; margin:1px 4px 1px 2px; font-size:1.1em; letter-spacing:-0.25em">'
    n, step = 0, 0.125
    while n <= len(history) - 1:
        t = n - int(n)
        r = history[int(n)] * (1 - t) + history[math.ceil(n)] * t
        style = ' top:%.2fpx; color:#%x%x3' % (7 - r * 15, 15 - r * 12.9, 3 + r * 7.9)
        ret += '<span style="position:relative;%s">%s</span>' % (style, '•')
        n += step
    ret += '</span>'
    return ret

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

def loc2str(voie, color):
    lut = { 'beige':    ['#d97', '#000'],
            'blanche':  ['#fff', '#000'],
            'bleue':    ['#68e', '#000'],
            'jaune':    ['#dd4', '#000'],
            'noire':    ['#333', '#eee'],
            'orange':   ['#ea4', '#000'],
            'rose':     ['#f9a', '#000'],
            'rouge':    ['#e44', '#000'],
            'saumon':   ['#e73', '#000'],
            'verte':    ['#6d6', '#000'],
            'violette': ['#a5e', '#000'],
          }
    style = lut[color] if color in lut else lut['blanche']
    return '<td style="background:%s;color:%s">%d %s</td>' % (style[0], style[1], voie, color)

def res2str(result):
    if result == 'OK':
        #return '<span style="color:#3a3">✔</span>'
        return '<span style="color:#3a3">✘</span>'
        #return '<span style="color:#3a3">☒</span>'
    else:
        #return '<span style="color:red">✗</span>'
        #return '<span style="color:#f33">×</span>'
        return '<span style="color:#f33">☐</span>'

print(header)

print('<table><tr><th>Grade</th>')
for d in days:
    print('<th>' + d + '</th>')
print('<th>Trend</th><th>Avg</th></tr>')

for g in reversed(sorted(grades)):
    print('<tr>' + gr2str(g))
    history, total, weight = [], 0, 0
    for d in days:
        s = '<td>'
        for voie, color, grade, result, comm in perfs[d]:
            if grade == g:
                s += res2str(result)
                if result == 'OK':
                    total += 1
                weight += 1
        history += [total / (weight + 1e-8)]
        total, weight = total / DECAY, weight / DECAY
        s += '</td>'
        print(s)
    ratio = total / weight * 100.0
    print('<td>%s</td><td>%.0f%%</td></tr>' % (hist2str(history), ratio, ))
print('</table>')

print('<p></p>')

print('<table><tr><th>Route</th><th>Grade</th><th>History</th><th>Notes</th>')
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
        print('<tr>' + loc2str(voie, color) + gr2str(g) + '<td>' + val + '</td><td>' + comments[key] + '</td></tr>')

print('</table>')

print(footer)

