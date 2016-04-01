#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pickle

all_entries = pickle.load(open("pskeys.p", "rb"))
print_order = ["NAME", "SUMMARY", "TYPE", "DEFAULT VALUE", "DESCRIPTION", "SECOM_KEY", "SECOM_DESCRIPTION"]

for entry in all_entries:
    for key in entry.keys():
        print ""
        for print_key in print_order:
            try:
                section_text = entry[print_key.lower()]
                print print_key.replace("_", " ")
                print "\t%s"%section_text.strip()
            except KeyError:
                pass
        print "="*78
