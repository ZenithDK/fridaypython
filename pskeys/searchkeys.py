#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle
from colored import fg, attr


if len(sys.argv) < 2:
    sys.stderr.write("Usage: %s <searchString1> ... [searchStringN]\n"%sys.argv[0])
    sys.exit(1)

all_entries = pickle.load(open("pskeys.p", "rb"))
print_order = ["NAME", "SUMMARY", "TYPE", "DEFAULT VALUE", "DESCRIPTION", "SECOM_KEY", "SECOM_DESCRIPTION"]

for entry in all_entries:
    match = False
    for key in entry.keys():
        if all(word in entry[key] for word in sys.argv[1:]):
            match = True
    if match:
        print ""
        for print_key in print_order:
            try:
                section_text = entry[print_key.lower()]
                for term in sys.argv[1:]:
                    section_text = section_text.replace(term, "%s%s%s"%(fg(9), term, attr(0)))

                print "%s%s%s"%(fg(3), print_key.replace("_", " "), attr(0))
                if print_key == "NAME":
                    print "\t%s%s%s"%(fg(15), section_text.strip(), attr(0))
                else:
                    print "\t%s"%section_text.strip()
            except KeyError:
                pass
        print "="*78
