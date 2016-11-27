#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, datetime
from dateutil.parser import parse
import config, tools

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

            r = r'\s*(\w*)\s*(\w*)\s*(\w*)\s*([+/0-9a-z]*)\s*(OK|--)\s*(.*)'
            m = re.match(r, l)
            if m:
                name, route, color, grade, result, comm = m.groups(1)
                self.names[name] = True
                if result == 'ET':
                    continue # Not supported yet
                self.perfs[cur_day] += [(name, route, color, grade, result, comm)]
                continue

            r = r'^###\s*([\w\s]*):*\s*(.*)'
            m = re.match(r, l)
            if m:
                user_date, _ = m.groups(1)
                date = parse(user_date).timestamp()
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

    def all_perfs(self, day, climber_name=None):
        return [p for p in self.perfs[day] if not climber_name or p[0] == climber_name]

    def print_history(self, climber_name):
        print('<table><tr><th>Grade</th><th>Trend</th><th>Avg</th>')
        volume = {}
        for d in self.all_days():
            print('<th>%s</th>' % (datetime.date.fromtimestamp(d).strftime('%d/%m') if self.all_perfs(d, climber_name) else ''))
            volume[d] = [0, 0]
        print('</tr>')

        for gn in reversed(tools.all_grades('4', '6b+')):
            # Only print lines for integer scores
            if gn != int(gn):
                continue
            g = tools.num_to_grade(gn)
            print('<tr>\n  ' + tools.grade_to_str(g))
            history, total, weight, ratio, prev_ratio = [], 0, 0, 0, 0
            s = ''
            for d in self.all_days():
                s += '  <td>'
                for name, route, color, grade, result, comm in self.all_perfs(d, climber_name):
                    graden = tools.grade_to_num(grade)
                    if abs(graden - gn) < 1:
                        percent = int(comm[0:2]) if comm and re.match('^\d\d%', comm) else 0
                        comm = ': %s' % comm if comm else ''
                        name = '[%s] ' % name if not climber_name else ''
                        if config.ENGLISH and color in tools.color_lut:
                            color = tools.color_lut[color]
                        if graden >= gn:
                            important = graden > gn
                            s += tools.res_to_str(result, percent, '%s%s %s (%s)%s' % (name, route, color, grade, comm), important)
                        k = 1 - abs(graden - gn)
                        if result == 'OK':
                            total += k
                            volume[d][0] += k
                        elif percent >= 50:
                            total += k * config.HALF_ROUTE_WEIGHT
                            volume[d][0] += k * 0.5
                        weight += k
                        volume[d][1] += k
                    elif graden > gn and result == 'OK':
                        total += config.OTHER_GRADE_WEIGHT
                        weight += config.OTHER_GRADE_WEIGHT
                    elif graden < gn and result != 'OK':
                        weight += config.OTHER_GRADE_WEIGHT
                if self.all_perfs(d, climber_name):
                    prev_ratio = ratio
                    ratio = total / (weight + 1e-8)
                    history += [(d, ratio)]
                if self.all_perfs(d, climber_name):
                    total, weight = total * config.DECAY, weight * config.DECAY
                s += '</td>\n'
            first_day = min(self.all_days())
            last_day = max(self.all_days())
            print('  <td>%s</td>\n  <td>%s</td>\n%s</tr>' % (tools.hist_to_str(history, first_day, last_day), tools.ratio_to_str(ratio, prev_ratio), s))

        #
        # Print best / average route
        #
        best, avg = {}, {}
        for d in self.all_days():
            best[d] = None
            avg[d] = []
            for name, route, color, grade, result, comm in self.all_perfs(d, climber_name):
                if result == 'OK':
                    if not best[d] or tools.grade_to_num(grade) > tools.grade_to_num(best[d]):
                        best[d] = grade
                    avg[d].append(tools.grade_to_num(grade))

        print('<tr><td style="background:#222" colspan="2"></td><th>Avg</th>')
        for d in self.all_days():
            avg_num = sum(avg[d]) / len(avg[d]) if avg[d] else 0
            print(tools.grade_to_str(tools.num_to_grade(avg_num)) if avg_num else '<td></td>')
        print('</tr>')

        print('<tr><td style="background:#222" colspan="2"></td><th>Best</th>')
        for d in self.all_days():
            print(tools.grade_to_str(best[d]) if best[d] else '<td></td>')
        print('</tr>')

        #
        # Print daily volume
        #
        print('<tr><td style="background:#222" colspan="2"></td><th>Vol</th>')
        for d in self.all_days():
            print('<td>%d/%d</td>' % tuple(volume[d]) if self.all_perfs(d, climber_name) else '<td></td>')
        print('</tr>')

        print('</table>')


    def print_routes(self, wanted_names):
        print('<table><tr><th>Route</th><th>Grade</th>')

        for name in wanted_names:
            print('<th class="notes notes' + name + ' notesAll">' + name + '</th>')
        for name in wanted_names:
            print('<th class="notes notes' + name + '">Notes</th>')

        aggregated = {}
        comments = {}
        for d in self.all_days():
            for name, route, color, grade, result, comm in self.all_perfs(d):
                if name not in wanted_names:
                    continue
                key = (route, color, grade)
                aggregated[key] = {}
                comments[key] = {}
                for name in wanted_names:
                    aggregated[key][name] = ''
                    comments[key][name] = ''
        for d in self.all_days():
            for name, route, color, grade, result, comm in self.all_perfs(d):
                if name not in wanted_names:
                    continue
                key = (route, color, grade)
                percent = int(comm[0:2]) if comm and re.match('^\d\d%', comm) else 0
                aggregated[key][name] += tools.res_to_str(result, percent, datetime.date.fromtimestamp(d).strftime('%d/%m') + (': ' + comm if comm else ''), False)
                if comm:
                    if comments[key][name]:
                        comments[key][name] += ' — '
                    comments[key][name] += datetime.date.fromtimestamp(d).strftime('%d/%m: ') + comm
        for gn in reversed(tools.all_grades('3', '6c+')):
            for key, val in sorted(aggregated.items()):
                route, color, grade = key
                if tools.grade_to_num(grade) != gn:
                    continue
                print('<tr>\n  ' + tools.route_to_str(route, color) + '\n  ' + tools.grade_to_str(grade))
                for name in wanted_names:
                    print('  <td class="notes notes' + name + ' notesAll">' + val[name] + '</td>')
                for name in wanted_names:
                    print('  <td class="notes notes' + name + '">' + comments[key][name] + '</td>')
                print('</tr>')

        print('</table>')

