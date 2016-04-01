#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import pickle

if len(sys.argv) < 3:
    sys.stderr.write("Usage: %s <pskeys.txt> <id_userkey.h>\n"%sys.argv[0])
    sys.exit(1)

try:
    fh = open(sys.argv[1], "r")
    all_contents = fh.readlines()
    fh.close()
except IOError:
    sys.stderr.write("Could not open file: %s\n"%sys.argv[1])
    sys.exit(1)

current_entry = {}
all_entries = []
description_section = False
keywords = ["NAME", "SUMMARY", "TYPE", "DEFAULT VALUE"]
secom_keys = {}

fh = open(sys.argv[2], "r")
while True:
    line = fh.readline()
    if not line:
        break

    line = line.strip()
    entry = re.findall("\#define ([a-zA-Z0-9_]+)\s+([0-9]+)\s+/\*(.*?)\*/", line)
    if len(entry) > 0:
        key = entry[0][0]
        number = int(entry[0][1])
        description = " ".join(entry[0][2].split())
        pskeyname = "PSKEY_"
        if number in range(0, 50):
            pskeyname += "USR%d"%number
        elif number in range(50, 100):
            pskeyname += "DSP%d"%(number-50)
        elif number in range(141, 150):
            pskeyname += "CONNLIB%d"%(number-100)

        secom_keys[pskeyname] = {"secom_key": key, "secom_description" : description }
fh.close()

for line_number, line_content in enumerate(all_contents):

    if description_section:
        if not current_entry.has_key("description"):
            current_entry["description"] = ""
        if line_content.strip() == "="*78:
            description_section = False
            all_entries.append(current_entry)
            current_entry = {}
            continue
        current_entry["description"] += line_content.rstrip()
        current_entry["description"] += "\n"
        continue

    if line_content.strip() == "DESCRIPTION":
        description_section = True
        continue

    if line_content.strip() in keywords:
        current_entry_content = all_contents[line_number+1].strip()
        current_entry[line_content.strip().lower()] = current_entry_content
        if line_content.strip() == "NAME":
            for key in secom_keys.keys():
                if key in current_entry["name"]:
                    current_entry.update(secom_keys[key])

pickle.dump(all_entries, open("pskeys.p", "wb"))
