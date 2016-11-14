#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, math, getopt
import tools

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
        grades[grade] = True
        if NAME and name.lower() != NAME:
            continue
        # Not supported yet
        if result == 'ET':
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
    ch = '•'
    #ch = '-'
    history = [0] + history
    ret = '<span style="display:block;height:17px;margin:1px 4px 1px 2px; font-size:0.65em; letter-spacing:-0.22em">'
    prev_r, n, step = -1, 0, 0.0625 * 1.25
    while n <= len(history) - 1:
        t = n - int(n)
        t = (3.0 - 2.0 * t) * t * t 
        r = history[int(n)] * (1 - t) + history[math.ceil(n)] * t
        style = ' top:%.2fpx; color:#%x%x3' % (13 - r * 17, int(15 - max(r * 2 - 1, 0) * 15.9), int(min(r * 2, 1) * 12.9))
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

def res2str(result, percent, comment, important):
    # Other character choices: █ ▒ ✔ ☒ ✗ × ☐ ✘ ∅ ✖
    if result == 'OK':
        color, ch = '#6d7', '✔'
    elif percent >= 50:
        color, ch = '#ec6', '✕'
    else:
        color, ch = '#f66', '✕'
    deco = ';text-shadow:0px 0px 2px #fff' if important else ''
    #deco += ';text-decoration:underline' if important else ''
    return '<span title="%s" style="color:%s;font-size:1.0em;font-weight:bold%s">%s</span>' % (comment, color, deco, ch)

print(header)

print('<div style="float:right">')
print(' |\n'.join('  <a href="%s.html">%s</a>' % (x.lower(), x) for x in sorted(names.keys()) + ['All']))
print('</div>')

print('<table><tr><th>Grade</th><th>Trend</th><th>Avg</th>')
for d in days:
    print('<th>%s</th>' % (d if perfs[d] else ''))
print('</tr>')

for gn in reversed(tools.all_grades('4', '6b+')):
    # Only print lines for integer scores
    if gn != int(gn):
        continue
    g = tools.num_to_grade(gn)
    print('<tr>\n  ' + tools.grade_to_str(g))
    history, total, weight, ratio, prev_ratio = [], 0, 0, 0, 0
    s = ''
    for d in days:
        s += '  <td>'
        for name, route, color, grade, result, comm in perfs[d]:
            graden = tools.grade_to_num(grade)
            if abs(graden - gn) < 1:
                percent = int(comm[0:2]) if comm and re.match('^\d\d%', comm) else 0
                comm = ': %s' % comm if comm else ''
                name = '[%s] ' % name if not NAME else ''
                if ENGLISH and color in color_lut:
                    color = color_lut[color]
                if graden >= gn:
                    important = graden > gn
                    s += res2str(result, percent, '%s%d %s (%s)%s' % (name, route, color, grade, comm), important)
                k = 1 - abs(graden - gn)
                if result == 'OK':
                    total += k
                elif percent >= 50:
                    total += k * HALF_ROUTE_WEIGHT
                weight += k
            elif graden > gn and result == 'OK':
                total += OTHER_GRADE_WEIGHT
                weight += OTHER_GRADE_WEIGHT
            elif graden < gn and result != 'OK':
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


print('<table><tr><th>Route</th><th>Grade</th>')

wanted_names = []
for name in sorted(names.keys()):
    if not NAME or name.lower() == NAME:
        wanted_names += [name]
#wanted_names = [NAME] if NAME else sorted(names.keys())
for name in wanted_names:
    print('<th>' + name + '</th>')
if NAME:
    print('<th>Notes</th>')

aggregated = {}
comments = {}
for d in days:
    for name, route, color, grade, result, comm in perfs[d]:
        key = (route, color, grade)
        aggregated[key] = {}
        comments[key] = {}
        for name in wanted_names:
            aggregated[key][name] = ''
            comments[key][name] = ''
for d in days:
    for name, route, color, grade, result, comm in perfs[d]:
        if name not in wanted_names:
            continue
        key = (route, color, grade)
        percent = int(comm[0:2]) if comm and re.match('^\d\d%', comm) else 0
        aggregated[key][name] += res2str(result, percent, d + ': ' + comm if comm else d, False)
        if comm:
            if comments[key][name]:
                comments[key][name] += ' — '
            comments[key][name] += d + ': ' + comm
for gn in reversed(tools.all_grades('3', '6c+')):
    for key, val in sorted(aggregated.items()):
        route, color, grade = key
        if tools.grade_to_num(grade) != gn:
            continue
        print('<tr>\n  ' + loc2str(route, color) + '\n  ' + tools.grade_to_str(grade))
        for name in wanted_names:
            print('  <td>' + val[name] + '</td>')
            if NAME:
                print('  <td>' + comments[key][name] + '</td>')
        print('</tr>')

print('</table>')

print(footer)

