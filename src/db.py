#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys

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

class Database:
    def __init__(self):
        self.names = {}
        self.days = []
        self.perfs = {}

        cur_day = None

        for l in sys.stdin.readlines():
            l = l.strip()
            if not l:
                continue

            r = r'\s*(\w*)\s*(\d*)\s*(\w*)\s*([+/0-9a-z]*)\s*(OK|--)\s*(.*)'
            m = re.match(r, l)
            if m:
                name, route, color, grade, result, comm = m.groups(1)
                self.names[name] = True
                if result == 'ET':
                    continue # Not supported yet
                self.perfs[cur_day] += [(name, int(route), color, grade, result, comm)]
                continue

            r = r'^###\s*(\d*) (\w*):*\s*(.*)'
            m = re.match(r, l)
            if m:
                day, month, _ = m.groups(1)
                date = '%02d/%02d' % (int(day), month_lut[month])
                cur_day = date
                if date not in self.days:
                    self.days += [date]
                if cur_day not in self.perfs:
                    self.perfs[cur_day] = []
                continue

    def all_names(self):
        return sorted(self.names.keys())

    def all_days(self):
        return self.days

    def all_perfs(self, day, name=None):
        return [p for p in self.perfs[day] if not name or p[0].lower() == name]

