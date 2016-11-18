#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re, sys, getopt
import config, tools, db

# Parse command line
config.NAME = None
optlist, args = getopt.getopt(sys.argv[1:], '', ['name=', 'english'])
for opt, arg in optlist:
    if opt == '--name':
        config.NAME = arg.lower()
    if opt == '--english':
        config.ENGLISH = True

# Some HTML data
print(r"""
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
""")

db = db.Database()

db.print_links()

db.print_history(config.NAME)

print('<p></p>')

wanted_names = []
for name in db.all_names():
    if not config.NAME or name.lower() == config.NAME:
        wanted_names += [name]
db.print_routes(wanted_names)

print(r"""
</body>
</html>
""")


