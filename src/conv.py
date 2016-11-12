#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, math, getopt

# How much previous days count
DECAY = 0.8

# How much success in a higher grade counts for lower grades
# and how much failure in lower grades counts for higher grades
OTHER_GRADE_WEIGHT = 0.5

# How much a >=50% failed route counts
HALF_ROUTE_WEIGHT = 0.3

# Should we translate color names to English?
ENGLISH = False

# Parse command line
NAME = None
optlist, args = getopt.getopt(sys.argv[1:], '', ['name=', 'english'])
for opt, arg in optlist:
    if opt == '--name':
        NAME = arg.lower()
    if opt == '--english':
        ENGLISH = True

color_lut = {
    'beige'    : 'beige',
    'blanche'  : 'white',
    'bleue'    : 'blue',
    'jaune'    : 'yellow',
    'noire'    : 'black',
    'orange'   : 'orange',
    'rose'     : 'pink',
    'rouge'    : 'red',
    'saumon'   : 'salmon',
    'verte'    : 'green',
    'violette' : 'purple',
}

month_lut = {
    'janvier'   : 1,
    'février'   : 2,
    'mars'      : 3,
    'avril'     : 4,
    'mai'       : 5,
    'juin'      : 6,
    'juillet'   : 7,
    'août'      : 8,
    'septembre' : 9,
    'octobre'   : 10,
    'novembre'  : 11,
    'décembre'  : 12,
}

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
    '6b+':    '#bebe40',
#    '6c':     '#aeae20',
#    '6c+':    '#9e9e00', # LOL
}

# Some HTML data
header = r"""
<html>
<head>
<style>
body {
    background: #222;
    color: #eee;
    font-family: sans-serif;
    margin: 30px 80px;
}

table {
    margin: 30px 0px;
}

a {
    color: #99d;
}

//tr:nth-child(even) { background: #e8f4ff; }
//tr:nth-child(odd) { background: #f8fcff; }
tr:nth-child(even) { background: #28343f; }
tr:nth-child(odd) { background: #383c3f; }

td {
    font-size: 0.9em;
    padding: 2px;
}

th {
    background: #bbb;
    color: #555;
}

table {
    border-collapse: separate;
    border-spacing: 2px 2px;
    min-width: 350px;
}

td.round { border-radius: 4px; }
table tr:last-child td.round:first-child { border-bottom-left-radius: 4px; }
table tr:last-child td.round:last-child { border-bottom-right-radius: 4px; }

</style>
</head>
<body>
"""

footer = r"""
</body>
</html>
"""

names = {}
grades = {}
days = []
perfs = {}
cur_day = None

for l in sys.stdin.readlines():
    l = l.strip()
    if not l:
        continue

    r = r'\s*(\w*)\s*(\d*)\s*(\w*)\s*([+/0-9a-z]*)\s*(OK|--)\s*(.*)'
    m = re.match(r, l)
    if m:
        name, route, color, grade, result, comm = m.groups(1)
        names[name] = True
        if grade == '4b':
            grade = '4+'
        if grade == '5c/6a':
            grade = '5c+/6a'
        grades[grade] = True
        if NAME and name.lower() != NAME:
            continue
        perfs[cur_day] += [(name, int(route), color, grade, result, comm)]
        continue

    r = r'^###\s*(\d*) (\w*):*\s*(.*)'
    m = re.match(r, l)
    if m:
        day, month, _ = m.groups(1)
        date = '%02d/%02d' % (int(day), month_lut[month])
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
    prev_r, n, step = -1, 0, 0.0625
    while n <= len(history) - 1:
        t = n - int(n)
        r = history[int(n)] * (1 - t) + history[math.ceil(n)] * t
        style = ' top:%.2fpx; color:#%x%x3' % (7 - r * 15, int(15 - max(r * 2 - 1, 0) * 15.9), int(min(r * 2, 1) * 12.9))
        # Use \n here to avoid super long lines…
        if int(64 * r) != int(64 * prev_r):
            if prev_r != -1:
                ret += '</span>'
            ret += '<span\nstyle="position:relative;%s">' % (style)
            prev_r = r
        ret += ch
        n += step
    ret += '</span></span>'
    return ret

def gr2str(grade):
    c = gr2str_lut[grade] if grade in gr2str_lut else 'white'
    return '<td class="round" style="color:#222;background:' + c + '">' + grade + '</td>'

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
    if ENGLISH and color in color_lut:
        color = color_lut[color]
    return '<td class="round" style="background:%s;color:%s">%d&nbsp;%s</td>' % (style[0], style[1], route, color)

def ratio2str(ratio, prev_ratio):
    ret = '%.0f%% ' % round(ratio * 100)
    delta = int((ratio - prev_ratio) * 100)
    ret += '(=)' if delta == 0 else '(%+d)' % delta
    return ret

def res2str(result, percent, comment):
    # Other character choices: █ ▒ ✔ ☒ ✗ × ☐ ✘ ∅ ✖
    if result == 'OK':
        color, ch = '#6d7', '✔'
    elif percent >= 50:
        color, ch = '#ec6', '✕'
    else:
        color, ch = '#f66', '✕'
    return '<span title="%s" style="color:%s;font-size:1.0em;font-weight:bold">%s</span>' % (comment, color, ch)

print(header)

print('<div style="float:right">')
print(' |\n'.join('  <a href="%s.html">%s</a>' % (x.lower(), x) for x in sorted(names.keys())))
print('</div>')

print('<table><tr><th>Grade</th><th>Trend</th><th>Avg</th>')
for d in days:
    print('<th>%s</th>' % (d if perfs[d] else ''))
print('</tr>')

for g in reversed(sorted(gr2str_lut.keys())):
    print('<tr>\n  ' + gr2str(g))
    history, total, weight, ratio, prev_ratio = [], 0, 0, 0, 0
    s = ''
    for d in days:
        s += '  <td>'
        for name, route, color, grade, result, comm in perfs[d]:
            if grade == g:
                percent = int(comm[0:2]) if comm and re.match('^\d\d%', comm) else 0
                comm = ': %s' % comm if comm else ''
                if ENGLISH and color in color_lut:
                    color = color_lut[color]
                s += res2str(result, percent, '%d %s%s' % (route, color, comm))
                if result == 'OK':
                    total += 1
                elif percent >= 50:
                    total += HALF_ROUTE_WEIGHT
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
        s += '</td>\n'
    print('  <td>%s</td>\n  <td>%s</td>\n%s</tr>' % (hist2str(history), ratio2str(ratio, prev_ratio), s))
print('</table>')

print('<p></p>')

print('<table><tr><th>Route</th><th>Grade</th><th>History</th><th>Notes</th>')
aggregated = {}
comments = {}
for d in days:
    for name, route, color, grade, result, comm in perfs[d]:
        key = (route, color, grade)
        aggregated[key] = ''
        comments[key] = ''
for d in days:
    for name, route, color, grade, result, comm in perfs[d]:
        key = (route, color, grade)
        percent = int(comm[0:2]) if comm and re.match('^\d\d%', comm) else 0
        aggregated[key] += res2str(result, percent, d + ': ' + comm if comm else d)
        if comm:
            if comments[key]:
                comments[key] += ' — '
            comments[key] += d + ': ' + comm
for g in reversed(sorted(grades)):
    for key, val in sorted(aggregated.items()):
        route, color, grade = key
        if grade != g:
            continue
        print('<tr>\n  ' + loc2str(route, color) + '\n  ' + gr2str(g) + '\n  <td>' + val + '</td>\n  <td>' + comments[key] + '</td>\n</tr>')

print('</table>')

print(footer)

