#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, datetime
from dateutil.parser import parse
import config, tools

class Database:
    def __init__(self):
        self.names = {}
        self.days = []
        self.attempts = {}
        self.cache = {} # contains history

        cur_day, cur_gym = 0.0, ''

        for l in sys.stdin.readlines():
            l = l.strip()
            if not l:
                continue

            r = r'\s*(\w*)\s*([^\s]*)\s*(\w*)\s*([+/0-9a-z]*)\s*(OK|--)\s*(.*)'
            m = re.match(r, l)
            if m:
                name, route, color, grade, result, comm = m.groups(1)
                self.names[name] = True
                if result == 'ET':
                    continue # Not supported yet
                self.attempts[cur_day] += [(name, cur_gym, route, color, grade, result, comm)]
                continue

            r = r'^###\s*([\w\s]*):*\s*(.*)'
            m = re.match(r, l)
            if m:
                user_date, cur_gym = m.groups(1)
                date = parse(user_date).timestamp()
                cur_day = date
                if date not in self.days:
                    self.days += [date]
                if cur_day not in self.attempts:
                    self.attempts[cur_day] = []
                continue

    def all_names(self):
        return sorted(self.names.keys())

    def all_days(self):
        return self.days

    def all_attempts(self, day, climber_name=None):
        return [a for a in self.attempts[day] if not climber_name or a[0] == climber_name]

    def print_history(self, climber_name):
        print('<table><tr><th>Grade</th><th>Trend</th><th>Avg</th>')
        climber_days = [d for d in self.all_days() if self.all_attempts(d, climber_name)]
        volume, perf = {}, {}
        for d in climber_days:
            print('<th>%s</th>' % (datetime.date.fromtimestamp(d).strftime('%d/%m')))
            volume[d] = [0, 0]
            perf[d] = 0
        print('</tr>')

        self.cache[climber_name] = {}

        for gn in reversed(tools.all_grades('4', '6c')):
            # Only print lines for integer scores
            if gn != int(gn):
                continue
            g = tools.num_to_grade(gn)
            print('<tr>\n  ' + tools.grade_to_str(g, 'td'))
            history = self.cache[climber_name][gn] = []
            total, weight, ratio, prev_ratio = 0, 0, 0, 0
            s = ''
            for d in climber_days:
                s += '  <td>'
                for name, gym, route, color, grade, result, comm in self.all_attempts(d, climber_name):
                    graden = tools.grade_to_num(grade)
                    delta = abs(graden - gn)
                    if delta < 1:
                        # If category is close to this route’s grade, its stats are directly affected
                        percent = int(comm[0:comm.find('%')]) if comm and re.match('^\d+%', comm) else 0
                        comm = ': %s' % comm if comm else ''
                        name = '[%s] ' % name if not climber_name else ''
                        if config.ENGLISH and color in tools.color_lut:
                            color = tools.color_lut[color]
                        if graden >= gn:
                            r = tools.res_to_str(result, percent, '%s%s %s %s (%s)%s' % (name, gym, route, color, grade, comm))
                            if graden > gn:
                                s += '<span style="position:relative;left:0px;top:-13px;">' + r + '</span>'
                            else:
                                s += r
                        t = 1 - delta
                        if result == 'OK':
                            total += t
                            volume[d][0] += t
                        #elif percent >= 50:
                        else:
                            total += t * percent / 100 * config.PARTIAL_ROUTE_WEIGHT
                            volume[d][0] += t * 0.5
                        weight += t
                        volume[d][1] += t
                    elif graden > gn and result == 'OK':
                        # If route was sent it counts as a success for lower grades, too
                        total += config.OTHER_GRADE_WEIGHT
                        weight += config.OTHER_GRADE_WEIGHT
                    elif graden < gn and result != 'OK':
                        # If route was failed it counts as a failure for higher grades, too
                        weight += config.OTHER_GRADE_WEIGHT
                if self.all_attempts(d, climber_name):
                    prev_ratio = ratio
                    ratio = total / (weight + 1e-8)
                    history += [(d, ratio)]
                perf[d] += 100.0 * (ratio - prev_ratio)
                if self.all_attempts(d, climber_name):
                    total, weight = total * config.DECAY, weight * config.DECAY
                s += '</td>\n'
            first_day = min(self.all_days())
            last_day = max(self.all_days())
            print('  <td>%s</td>\n  <td>%s</td>\n%s</tr>' % (tools.hist_to_str(history, first_day, last_day), tools.ratio_to_str(ratio, prev_ratio), s))

        #
        # Print best / average route
        #
        best, avg = {}, {}
        for d in climber_days:
            best[d] = None
            avg[d] = []
            for name, gym, route, color, grade, result, comm in self.all_attempts(d, climber_name):
                if result == 'OK':
                    if not best[d] or tools.grade_to_num(grade) > tools.grade_to_num(best[d]):
                        best[d] = grade
                    avg[d].append(tools.grade_to_num(grade))

        print('<tr><td style="background:#222" colspan="2"></td><th>Avg</th>')
        for d in climber_days:
            avg_num = sum(avg[d]) / len(avg[d]) if avg[d] else 0
            print(tools.grade_to_str(tools.num_to_grade(avg_num), 'td') if avg_num else '<td></td>')
        print('</tr>')

        print('<tr><td style="background:#222" colspan="2"></td><th>Best</th>')
        for d in climber_days:
            print(tools.grade_to_str(best[d], 'td') if best[d] else '<td></td>')
        print('</tr>')

        #
        # Print daily volume
        #
        print('<tr><td style="background:#222" colspan="2"></td><th>Vol</th>')
        for d in climber_days:
            print('<td>%d/%d</td>' % tuple(volume[d]) if self.all_attempts(d, climber_name) else '<td></td>')
        print('</tr>')

        #
        # Print stats variation
        #
        print('<tr><td style="background:#222" colspan="2"></td><th>Perf</th>')
        is_first_day = True
        for d in climber_days:
            out = '<td></td>'
            if not is_first_day:
                out = '<td style="color:#%s">%+d</td>' % ('6d7' if perf[d] > 0 else 'ec6' if perf[d] > -10 else 'f66', round(perf[d])) if perf[d] else '<td>=</td>'
            is_first_day = False
            print(out)
        print('</tr>')

        print('</table>')


    def print_suggestions(self, climber_name):
        history = self.cache[climber_name]
        first = 1000
        for gn in tools.all_grades('4', '6c'):
            try:
                cur = history[gn][-1][1]
                if gn < first and cur < 0.5:
                    first = gn
            except:
                pass

        # List routes; 0: never tried, 1: failed, 2: succeeded
        summary = {}
        aggregated = {}
        for d in self.all_days():
            for name, gym, route, color, grade, result, comm in self.all_attempts(d):
                key = (gym, route, color, grade)
                percent = int(comm[0:comm.find('%')]) if comm and re.match('^\d+%', comm) else 0
                if key not in summary:
                    summary[key] = 0
                    aggregated[key] = ''
                if name == climber_name:
                    summary[key] = max(summary[key], 1)
                    if result == 'OK':
                        summary[key] = max(summary[key], 2)
                    aggregated[key] += tools.res_to_str(result, percent, datetime.date.fromtimestamp(d).strftime('%d/%m') + (': ' + comm if comm else ''))

        print('<hr style="opacity:0;clear:both"/>')
        cat = [("Consolidate", False, 0, first - 1),
               ("Improve",     False, first - 1, first),
               ("Maybe",       True,  first, first + 1)]
        for title, last, a, b in cat:
            print('<div style="margin-right: 30px; float:left">' if not last else '<div>')
            print('<h2>%s: %s</h2>' % (title, tools.grade_to_str(tools.num_to_grade(b), 'span')))
            print('<table><tr><th>Gym</th><th>Route</th><th>Grade</th><th></th></tr>')
            for gn in reversed(tools.all_grades('3', '6c+')):
                for key, val in sorted(summary.items()):
                    gym, route, color, grade = key
                    if tools.grade_to_num(grade) != gn:
                        continue
                    if val == 0 and tools.grade_to_num(grade) < first - 2:
                        continue
                    if val not in [0, 1] or tools.grade_to_num(grade) > b \
                                         or tools.grade_to_num(grade) <= a:
                        continue
                    print('<tr><td>' + gym + '</td>\n  ' + tools.route_to_str(route, color) + '\n  ' + tools.grade_to_str(grade, 'td'))
                    print('  <td>' + aggregated[key] + '</td>')
                    print('</tr>')
            print('</table>')
            print('</div>')
        print('<hr style="opacity:0;clear:both"/>')


    def print_routes(self, wanted_names, with_notes=True):
        print('<table><tr><th>Gym</th><th>Route</th><th>Grade</th>')

        if with_notes:
            for name in wanted_names:
                print('<th class="notes notes' + name + ' notesAll">' + name + '</th>')
            for name in wanted_names:
                print('<th class="notes notes' + name + '">Notes</th>')

        aggregated = {}
        comments = {}
        for d in self.all_days():
            for name, gym, route, color, grade, result, comm in self.all_attempts(d):
                if name not in wanted_names:
                    continue
                key = (gym, route, color, grade)
                aggregated[key] = {}
                comments[key] = {}
                for name in wanted_names:
                    aggregated[key][name] = ''
                    comments[key][name] = ''
        for d in self.all_days():
            for name, gym, route, color, grade, result, comm in self.all_attempts(d):
                if name not in wanted_names:
                    continue
                key = (gym, route, color, grade)
                percent = int(comm[0:comm.find('%')]) if comm and re.match('^\d+%', comm) else 0
                aggregated[key][name] += tools.res_to_str(result, percent, datetime.date.fromtimestamp(d).strftime('%d/%m') + (': ' + comm if comm else ''))
                if comm:
                    if comments[key][name]:
                        comments[key][name] += ' — '
                    comments[key][name] += datetime.date.fromtimestamp(d).strftime('%d/%m: ') + comm
        for gn in reversed(tools.all_grades('3', '6c+')):
            for key, val in sorted(aggregated.items()):
                gym, route, color, grade = key
                if tools.grade_to_num(grade) != gn:
                    continue
                print('<tr><td>' + gym + '</td>\n  ' + tools.route_to_str(route, color) + '\n  ' + tools.grade_to_str(grade, 'td'))
                if with_notes:
                    for name in wanted_names:
                        print('  <td class="notes notes' + name + ' notesAll">' + val[name] + '</td>')
                    for name in wanted_names:
                        print('  <td class="notes notes' + name + '">' + comments[key][name] + '</td>')
                print('</tr>')

        print('</table>')

