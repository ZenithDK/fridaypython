#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

if len(sys.argv) < 2:
    sys.stderr.write("Usage %s <config-file>\n"%sys.argv[0])
    sys.exit(1)

config_fh = open(sys.argv[1], "r")
format_mode = False
format_section = []

def print_formatted(section):
    column_lengths = []
    for line in section:
        if line.strip().startswith("/*") and not any(word in line for word in ["<event>", "<state>"]):
            continue
        for i, item in enumerate(line.split(",")):
            try:
                column_lengths[i] = max(len(item.strip()), column_lengths[i])
            except IndexError:
                column_lengths.append(len(item.strip()))
    for line in section:
        print " ",
        all_segments = line.split(",")
        try:
            if all_segments[1].strip() != "0" and all_segments[1].strip() == all_segments[2].strip():
                all_segments[2] = "0"
        except IndexError:
            pass
        for i, segment in enumerate(all_segments):
            if i > 0:
                print ",",
            if segment.strip().endswith("\\"):
                sys.stdout.write(segment.strip())
            else:
                sys.stdout.write(segment.strip().ljust(column_lengths[i]))


        print ""

while True:
    line = config_fh.readline()
    if not line:
        break
    
    if format_mode:
        format_section.append(line.strip())
    else:
        print line.rstrip()

    if "define" in line and (any(word in line for word in ["STATETABLE", "EVENTTABLE"])):
        format_mode = True
        format_section = []

    if format_mode and line.strip().endswith("}"):
        format_mode = False
        print_formatted(format_section)

config_fh.close()
