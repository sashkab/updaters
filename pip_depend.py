#!/usr/bin/env python

# Dependency finder for python packages

import pip
from pprint import pprint

d = {}

for dist in pip.get_installed_distributions():
    p = dist.project_name
    rev_dep = [
        pkg.project_name for pkg in pip.get_installed_distributions() if p in 
        [requirement.project_name for requirement in pkg.requires()]
    ]

    for x in rev_dep:
        if p in d:
            d[p].append(x)
        else:
            d[p] = [x]

pprint(d)

