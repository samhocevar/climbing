#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import config

gr2str_lut = {
    '3':       (1,   '#f15189'),
    '3+':      (2,   '#e13169'),
    '4':       (3,   '#5189f1'),
    '4+':      (4,   '#3169e1'),
    '4b':      (4,   '#3169e1'),
    '4+/5a':   (4.5, '#1149d1'),
    '5a':      (5,   '#a0eea0'),
    '5a/+':    (5.5, '#90e690'),
    '5a+':     (6,   '#80de80'),
    '5a+/b':   (6.5, '#70d670'),
    '5b':      (7,   '#60ce60'),
    '5b/+':    (7.5, '#50c650'),
    '5b+':     (8,   '#40be40'),
    '5b+/c':   (8.5, '#30b630'),
    '5c':      (9,   '#20ae20'),
    '5c/+':    (9.5, '#10a610'),
    '5c+':    (10,   '#009e00'),
    '5c+/6a': (10.5, '#008e00'),
    '5c/6a':  (10.5, '#008e00'),
    '6a':     (11,   '#eeeea0'),
    '6a/+':   (11.5, '#e6e690'),
    '6a+':    (12,   '#dede80'),
    '6a+/b':  (12.5, '#d6d670'),
    '6b':     (13,   '#cece60'),
    '6b/+':   (13.5, '#c6c650'),
    '6b+':    (14,   '#bebe40'),
    '6b+/c':  (14.5, '#b6b630'),
    '6c':     (15,   '#aeae20'),
    '6c/+':   (15.5, '#a6a610'),
    '6c+':    (16,   '#9e9e00'), # LOL
    '6c+/7a': (16.5, '#969600'),
    '7a':     (17,   '#a0eeee'),
    '7a/+':   (17.5, '#90e6e6'),
    '7a+':    (18,   '#80dede'),
    '7a+/b':  (18.5, '#70d6d6'),
    '7b':     (19,   '#60cece'),
    '7b/+':   (19.5, '#50c6c6'),
    '7b+':    (20,   '#40bebe'),
    '7b+/c':  (20.5, '#30b6b6'),
    '7c':     (21,   '#20aeae'),
    '7c/+':   (21.5, '#10a6a6'),
    '7c+':    (22,   '#009e9e'),
    '8a':     (23,   '#eea0ee'),
    '8a+':    (24,   '#de80de'),
    '8b':     (25,   '#ce60ce'),
    '8b+':    (26,   '#be40be'),
    '8c':     (27,   '#ae20ae'),
    '8c+':    (28,   '#9e009e'),
}

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
    c = gr2str_lut[grade][1] if grade in gr2str_lut else 'white'
    return '<td class="round" style="color:#222;background:' + c + '">' + grade + '</td>'

def grade_to_num(grade):
    return gr2str_lut[grade][0] if grade in gr2str_lut else 0

def num_to_grade(num):
    best, bestnum = None, 0
    for key in sorted(gr2str_lut):
        if gr2str_lut[key][0] == num:
            return key
        elif not best or abs(gr2str_lut[key][0] - num) < abs(gr2str_lut[best][0] - num):
            best = key
    return best

def all_grades(min = '3', max = '6c+'):
    a1, a2 = grade_to_num(min), grade_to_num(max)
    k = []
    for key in gr2str_lut:
       if gr2str_lut[key][0] >= a1 and gr2str_lut[key][0] <= a2:
           k.append(gr2str_lut[key][0])
    return sorted(set(k))

def res_to_str(result, percent, comment, important):
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
    prev_d, prev_r, prev_n1, prev_color = 0, -1, 0, None
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
            color = '#%x%x3' % (int(15 - max(r * 2 - 1, 0) * 15.9), int(min(r * 2, 1) * 12.9))
            style = ' top:%.2fpx; color:%s' % (13 - r * 17, color)
        if int(64 * r) != int(64 * prev_r) or color != prev_color:
            if prev_r != -1:
                ret += '</span>'
            # Use \n here to avoid super long lines…
            ret += '<span\nstyle="position:relative;%s">' % (style)
        if n1 != prev_n1 or (d >= history[n1][0] and prev_d < history[n1][0]):
            ret += '<span\nstyle="color:white">/</span>'
            #ret += '<span>/</span>'
        else:
            ret += ch
        prev_d, prev_r, prev_n1, prev_color = d, r, n1, color
        if d > last_day:
            break
        # Normal step is 1, but we make recent days print more dots
        mult = 1.3 * pow(0.5 + (last_day - d) / (last_day - first_day), 2.0)
        d += mult * 3600.0 * 24.0 / DOTS_PER_DAY
    ret += '</span></span>'
    return ret

