#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, math

# How much previous days count
DECAY = 0.8

# How much success in a higher grade counts for lower grades
# and how much failure in lower grades counts for higher grades
OTHER_GRADE_WEIGHT = 0.5

header = r"""
<html>
<head>
<style>
body {
    background-color: #def;
    font-family: sans-serif;
}
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
        route, color, grade, result, comm = m.groups(1)
        if grade == '4b':
            grade = '4+'
        grades[grade] = True
        perfs[cur_day] += [(int(route), color, grade, result, comm)]
        continue

    r = r'\s*([a-z0-9]* \w\w\w)\w*: *(.*)'
    m = re.match(r, l)
    if m:
        date, comment = m.groups(1)
        cur_day = date
        if date not in days:
            days += [date]
        if cur_day not in perfs:
            perfs[cur_day] = []
        continue

def hist2str(history):
    #ch = '•'
    ch = '-'
    history = [0] + history
    ret = '<span style="display:block; margin:1px 4px 1px 2px; font-size:1.1em; letter-spacing:-0.25em">'
    n, step = 0, 0.0625
    while n <= len(history) - 1:
        t = n - int(n)
        r = history[int(n)] * (1 - t) + history[math.ceil(n)] * t
        style = ' top:%.2fpx; color:#%x%x3' % (7 - r * 15, 15 - max(r * 2 - 1, 0) * 15.9, 0 + min(r * 2, 1) * 12.9)
        ret += '<span style="position:relative;%s">%s</span>' % (style, ch)
        n += step
    ret += '</span>'
    return ret

gr2str_lut = {
    '4':      '#5189f1',
    '4+':     '#3169e1',
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
#    '6b+':    '#bebe40',
#    '6c':     '#aeae20',
#    '6c+':    '#9e9e00', # LOL
}

def gr2str(grade):
    c = gr2str_lut[grade] if grade in gr2str_lut else 'white'
    return '<td style="background: ' + c + '">' + grade + '</td>'

def loc2str(route, color):
    lut = { 'beige':    ['#d97', '#000'],
            'blanche':  ['#fff', '#000'],
            'bleue':    ['#68e', '#000'],
            'jaune':    ['#dd4', '#000'],
            'noire':    ['#333', '#eee'],
            'orange':   ['#f82', '#000'],
            'rose':     ['#f7a', '#000'],
            'rouge':    ['#e44', '#000'],
            'saumon':   ['#fa8', '#000'],
            'verte':    ['#6d6', '#000'],
            'violette': ['#a5e', '#000'],
          }
    style = lut[color] if color in lut else lut['blanche']
    return '<td style="background:%s;color:%s">%d&nbsp;%s</td>' % (style[0], style[1], route, color)

def ratio2str(ratio, prev_ratio):
    ret = '%.0f%% ' % (ratio * 100)
    delta = int((ratio - prev_ratio) * 100)
    ret += '(=)' if delta == 0 else '(%+d)' % delta
    return ret

def res2str(result):
    if result == 'OK':
        #return '<span style="color:#3a3">✔</span>'
        return '<span style="color:#3a3">✘</span>'
        #return '<span style="color:#3a3">☒</span>'
    else:
        #return '<span style="color:red">✗</span>'
        #return '<span style="color:#f33">×</span>'
        #return '<span style="color:#f33">☐</span>'
        return '<span style="color:#f33">∅</span>'

print(header)

print('<table><tr><th>Grade</th><th>Trend</th><th>Avg</th>')
for d in days:
    print('<th>%s</th>' % (d if perfs[d] else ''))
print('</tr>')

for g in reversed(sorted(gr2str_lut.keys())):
    print('<tr>' + gr2str(g))
    history, total, weight, ratio = [], 0, 0, 0
    s = ''
    for d in days:
        s += '<td>'
        for route, color, grade, result, comm in perfs[d]:
            if grade == g:
                s += res2str(result)
                if result == 'OK':
                    total += 1
                weight += 1
            elif grade > g and result == 'OK':
                total += OTHER_GRADE_WEIGHT
                weight += OTHER_GRADE_WEIGHT
            elif grade < g and result != 'OK':
                weight += OTHER_GRADE_WEIGHT
        if perfs[d]:
            prev_ratio = ratio
        ratio = total / (weight + 1e-8)
        history += [ratio]
        if perfs[d]:
            total, weight = total * DECAY, weight * DECAY
        s += '</td>'
    print('<td style="background-color:black;">%s</td><td>%s</td>%s</tr>' % (hist2str(history), ratio2str(ratio, prev_ratio), s))
print('</table>')

print('<p></p>')

print('<table><tr><th>Route</th><th>Grade</th><th>History</th><th>Notes</th>')
aggregated = {}
comments = {}
for d in days:
    for route, color, grade, result, comm in perfs[d]:
        key = (route, color, grade)
        aggregated[key] = ''
        comments[key] = ''
for d in days:
    for route, color, grade, result, comm in perfs[d]:
        key = (route, color, grade)
        aggregated[key] += res2str(result)
        if comm:
            if comments[key]:
                comments[key] += ' — '
            comments[key] += d + ': ' + comm
for g in reversed(sorted(grades)):
    for key, val in sorted(aggregated.items()):
        route, color, grade = key
        if grade != g:
            continue
        print('<tr>' + loc2str(route, color) + gr2str(g) + '<td>' + val + '</td><td>' + comments[key] + '</td></tr>')

print('</table>')

print(footer)

