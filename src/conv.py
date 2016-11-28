#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, getopt
import config, tools, db

# Parse command line
optlist, args = getopt.getopt(sys.argv[1:], '', ['english'])
for opt, arg in optlist:
    if opt == '--english':
        config.ENGLISH = True

# Some HTML data
print("""
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
    color: #555;
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

.active-tab {
    background: #fff;
}

.tab {
    border-radius: 4px;
    padding: 2px 6px;
    font-weight: bold;
}

td.round { border-radius: 4px; }
table tr:last-child td.round:first-child { border-bottom-left-radius: 4px; }
table tr:last-child td.round:last-child { border-bottom-right-radius: 4px; }
</style>

<script>
function open_tab(id) {
    var l = document.getElementsByClassName('history');
    for (var i = 0; i < l.length; ++i) {
        l[i].style.display = "none";
    }
    l = document.getElementsByClassName('tab');
    for (var i = 0; i < l.length; ++i) {
        l[i].style.backgroundColor = "#bbb";
        l[i].style.color = "#555";
        //l[i].class = "tab";
    }
    document.getElementById(id).style.display = "block";
    document.getElementById('tab' + id).style.backgroundColor = "#555";
    document.getElementById('tab' + id).style.color = "#bbb";
    //document.getElementById('tab' + id).class = "tab active-tab";

    var l = document.getElementsByClassName('notes');
    for (var i = 0; i < l.length; ++i) {
        l[i].style.display = l[i].classList.contains('notes' + id) ? "" : "none";
        //l[i].style.visibility = l[i].classList.contains('notes' + id) ? "visible" : "collapse";
    }
}
function nav_tab(direction) {
    var l = document.getElementsByClassName('history');
    var n = l.length - 1; // don’t cycle through the “All” button
    for (var i = 0; i < n; ++i) {
        if (l[i].style.display == "block") {
            open_tab(l[(i + direction + n) % n].id);
            return;
        }
    }
}
document.onkeydown = function(e) {
    var e = e || window.event;
    if (e.which == 37) { // left
        nav_tab(-1);
    }
    else if (e.which == 39) { // right
        nav_tab(1);
    }
}
</script>
</head>
<body>
""")

db = db.Database()

button = '''<a href="javascript:void(0)" onClick="open_tab('%s')"><span class="tab" id="tab%s">%s</span></a> '''
print('<span>')
print('<a style="text-decoration:none" href="javascript:void(0)" onClick="nav_tab(-1)"><span class="tab">◀</span></a>')
for name in db.all_names():
    print(button % (name, name, name))
print('<a style="text-decoration:none" href="javascript:void(0)" onClick="nav_tab(1)"><span class="tab">▶</span></a>')
print('</span>')
print('<span style="margin:0 20px">')
print(button % ('All', 'All', 'All'))
print('</span>')

for name in db.all_names() + [None]:
    print('<div class="history" id="%s">' % (name or 'All'))
    db.print_history(name)
    print('</div>')

print('<script>open_tab("%s")</script>' % (db.all_names()[0]))

wanted_names = []
for name in db.all_names():
    wanted_names += [name]
db.print_routes(wanted_names)

print('<script>open_tab("%s")</script>' % (db.all_names()[0]))

print("""
</body>
</html>
""")

