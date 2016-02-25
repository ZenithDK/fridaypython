#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import sys
from colored import fg, attr

if len(sys.argv) < 3:
    sys.stderr.write("Usage: %s <pickle-file> <string1> [string2] ... [stringN]\n"%sys.argv[0])
    sys.exit(1)

all_contents = pickle.load(open(sys.argv[1], "rb"))

try:
    for key in all_contents.keys():
        allContent = ""
        for item in all_contents[key]:
            allContent += item["message"]

        if all(word.lower() in allContent.lower() for word in sys.argv[2:]):
            print "%sMatch: https://www.csrsupport.com/issue.php?iid=%s%s"%(fg(11), key, attr(0))
            for item in all_contents[key]:
                message = item["message"]
                for term in sys.argv[2:]:
                    message = message.replace(term, "%s%s%s"%(fg(9), term, attr(0)))
                print ("%s%s%s - %s%s%s:\n%s"%(fg(3), item["date"], attr(0), fg(4), item["author"], attr(0), message)).encode("ascii", "ignore")
            print "%s====%s"%(fg(11), attr(0))
except IOError:
    sys.exit(1)
