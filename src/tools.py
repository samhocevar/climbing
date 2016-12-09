#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math, datetime
import config

gr2str_lut = {
    '3':       2,
    '3+':      3,
    '4':       4,
    '4+':      5,
    '4b':      5,
    '4+/5a':   5.5,

    '5a':      6,
    '5a/+':    6.5,
    '5a+':     7,
    '5a+/b':   7.5,
    '5b':      8,
    '5b/+':    8.5,
    '5b+':     9,
    '5b+/c':   9.5,
    '5c':     10,
    '5c/+':   10.5,
    '5c+':    11,
    '5c+/6a': 11.5,
    '5c/6a':  11.5,

    '6a':     12,
    '6a/+':   12.5,
    '6a+':    13,
    '6a+/b':  13.5,
    '6b':     14,
    '6b/+':   14.5,
    '6b+':    15,
    '6b+/c':  15.5,
    '6c':     16,
    '6c/+':   16.5,
    '6c+':    17,
    '6c+/7a': 17.5,

    '7a':     18,
    '7a/+':   18.5,
    '7a+':    19,
    '7a+/b':  19.5,
    '7b':     20,
    '7b/+':   20.5,
    '7b+':    21,
    '7b+/c':  21.5,
    '7c':     22,
    '7c/+':   22.5,
    '7c+':    23,

    '8a':     24,
    '8a+':    25,
    '8b':     26,
    '8b+':    27,
    '8c':     28,
    '8c+':    29,
}

def num_to_color(num):
    x = num % 6.0
    u, v = int(0xff - 16 * x), int(0xb0 - 28 * x)
    return '#%2x%2x%2x' % [(u, v, u), (v, u, v), (u, u, v), (v, u, u), (u, v, v)][int(num / 6)]

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

def grade_to_str(grade):
    c = num_to_color(gr2str_lut[grade]) if grade in gr2str_lut else 'white'
    return '<td class="round" style="color:#222;background:' + c + '">' + grade + '</td>'

def grade_to_num(grade):
    return gr2str_lut[grade] if grade in gr2str_lut else 0

def num_to_grade(num):
    best, bestnum = None, 0
    for key in sorted(gr2str_lut):
        if gr2str_lut[key] == num:
            return key
        elif not best or abs(gr2str_lut[key] - num) < abs(gr2str_lut[best] - num):
            best = key
    return best

def all_grades(min = '3', max = '6c+'):
    a1, a2 = grade_to_num(min), grade_to_num(max)
    k = []
    for key in gr2str_lut:
       if gr2str_lut[key] >= a1 and gr2str_lut[key] <= a2:
           k.append(gr2str_lut[key])
    return sorted(set(k))

def res_to_str(result, percent, comment):
    # Other character choices: █ ▒ ✔ ☒ ✗ × ☐ ✘ ∅ ✖
    if result == 'OK':
        color, ch = '#6d7', '✔'
    else:
        color = '#%x%x3' % (int(31 - max(percent / 75.0, 1) * 15.9), int(min(percent / 75.0, 1) * 12.9))
        ch = '✕'
    return '<span title="%s" style="color:%s;font-size:1.0em;cursor:default;font-weight:bold">%s</span>' % (comment, color, ch)

def route_to_str(route, color):
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
    if config.ENGLISH and color in color_lut:
        color = color_lut[color]
    return '<td class="round" style="background:%s;color:%s">%s&nbsp;%s</td>' % (style[0], style[1], route, color)

def ratio_to_str(ratio, prev_ratio):
    ret = '%.0f%%&nbsp;' % round(ratio * 100)
    delta = int((ratio - prev_ratio) * 100)
    ret += '(=)' if delta == 0 else '(%+d)' % delta
    return ret

def hist_to_str(history, first_day, last_day):
    ch = '•'
    #ch = '-'
    ret = '<span style="display:block;height:17px;margin:1px 4px 1px 2px; font-size:0.65em; letter-spacing:-0.22em">'
    DOTS_PER_DAY = 3
    run, prev_d, prev_r, prev_n1, prev_color = 0, 0, -1, 0, None
    d, step = first_day, 0.0625 * 1.25
    while True:
        # Find closest data
        n1 = 0
        while n1 + 1 < len(history) and history[n1 + 1][0] < d:
            n1 += 1
        n2 = min(n1 + 1, len(history) - 1)
        if n1 == n2:
            t = 0
        else:
            t = (d - history[n1][0]) / (history[n2][0] - history[n1][0])
        #t = n - int(n)
        t = (3.0 - 2.0 * t) * t * t
        if d < history[n1][0]:
            r = -1
            color = 'transparent'
            style = ' color:' + color
        else:
            r = history[n1][1] * (1 - t) + history[n2][1] * t
            color = '#%x%x3' % (int(31 - max(r * 2, 1) * 15.9), int(min(r * 2, 1) * 12.9))
            style = ' top:%.2fpx; color:%s' % (13 - r * 17, color)
        if int(64 * r) != int(64 * prev_r) or color != prev_color or run > 20:
            if prev_r != -1:
                ret += '</span>'
            # Use \n here to avoid super long lines…
            ret += '<span\ntitle="%s: %.0f%%" style="position:relative;%s">' % (datetime.date.fromtimestamp(d).strftime('%d/%m'), r * 100, style)
            prev_r = r
            run = 0
        if n1 != prev_n1 or (d >= history[n1][0] and prev_d < history[n1][0]):
            ret += '<span\nstyle="color:white">/</span>'
            #ret += '<span>/</span>'
        else:
            ret += ch
            run += 1
        prev_d, prev_n1, prev_color = d, n1, color
        if d > last_day:
            break
        # Normal step is 1, but we make recent days print more dots
        mult = 1.3 * pow(0.5 + (last_day - d) / (last_day - first_day), 2.0)
        d += mult * 3600.0 * 24.0 / DOTS_PER_DAY
    ret += '</span></span>'
    return ret

