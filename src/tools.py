#!/usr/bin/env python3
# -*- coding: utf-8 -*-

gr2str_lut = {
    '3':       (1,   '#f15189'),
    '3+':      (2,   '#e13169'),
    '4':       (3,   '#5189f1'),
    '4+':      (4,   '#3169e1'),
    '4b':      (4,   '#3169e1'),
    '4+/5a':   (4.5, '#1149d1'),
    '5a':      (5,   '#a0eea0'),
    '5a+':     (6,   '#80de80'),
    '5a+/b':   (6.5, '#70d670'),
    '5b':      (7,   '#60ce60'),
    '5b/+':    (7.5, '#50c650'),
    '5b+':     (8,   '#40be40'),
    '5b+/c':   (8.5, '#30b630'),
    '5c':      (9,   '#20ae20'),
    '5c+':    (10,   '#009e00'),
    '5c+/6a': (10.5, '#008e00'),
    '5c/6a':  (10.5, '#008e00'),
    '6a':     (11,   '#eeeea0'),
    '6a/+':   (11.5, '#e6e690'),
    '6a+':    (12,   '#dede80'),
    '6a+/b':  (12.5, '#d6d670'),
    '6b':     (13,   '#cece60'),
    '6b+':    (14,   '#bebe40'),
    '6b+/c':  (14.5, '#b6b630'),
    '6c':     (15,   '#aeae20'),
    '6c+':    (16.0, '#9e9e00'), # LOL
}

def grade_to_str(grade):
    c = gr2str_lut[grade][1] if grade in gr2str_lut else 'white'
    return '<td class="round" style="color:#222;background:' + c + '">' + grade + '</td>'

def grade_to_num(grade):
    return gr2str_lut[grade][0] if grade in gr2str_lut else 0

def num_to_grade(num):
    for key in sorted(gr2str_lut):
        if gr2str_lut[key][0] == num:
            return key
    return 'unknown'

def all_grades(min = '3', max = '6c+'):
    a1, a2 = grade_to_num(min), grade_to_num(max)
    k = []
    for key in gr2str_lut:
       if gr2str_lut[key][0] >= a1 and gr2str_lut[key][0] <= a2:
           k.append(gr2str_lut[key][0])
    return sorted(set(k))

