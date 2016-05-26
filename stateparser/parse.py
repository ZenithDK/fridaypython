#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import os
import ConfigParser
import ast

from utils import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description="Event/State log parser",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "log_file",
        help="Logfile to parse",
        nargs=1
    )

    parser.add_argument(
        "-m",
        "--mapping",
        dest="mapping_file",
        help="File containing mappings between enums and header-files",
        default="default_mappings.ini"
    )

    parser.add_argument(
        "-p",
        "--project",
        dest="project",
        help="Specify project folder",
        default="."
    )

    args = parser.parse_args(sys.argv[1:])

    mappings = ConfigParser.ConfigParser()

    try:
        mappings.readfp(open(args.mapping_file, "r"))
    except IOError, e:
        sys.stderr.write("Error: Could not open: %s\n" % e.filename)
        sys.exit(1)

    if not mappings.has_section("mappings"):
        sys.stderr.write("Error: Couldn't find a 'mappings' section in '%s'\n" % args.mapping_file)
        sys.exit(1)

    try:
        state_machine_enums = enum_parser(os.path.join(
            args.project,
            "vmkit",
            "src",
            "secom",
            "state_machine",
            "state_machine.h"
        ))
        getattr(state_machine_enums, "ModuleIdentifier")
    except IOError, e:
        sys.stderr.write("Error: Could not open: %s\n" % e.filename)
        sys.exit(1)
    except AttributeError:
        sys.stderr.write("Error: 'state_machine.h' doesn't contain an enum for 'ModuleIdentifier'\n")
        sys.exit(1)

    all_tables = {"STATE_LIST": {}, "EVENT_LIST": {}}
    max_lengths = {"STATE_LIST": 0, "EVENT_LIST": 0, "module_identifier": 0}
    indents = {}

    for module_identifier in state_machine_enums.ModuleIdentifier.get_all_strings():
        source_files = ast.literal_eval(mappings.get("mappings", module_identifier))
        indents[module_identifier] = []
        if len(module_identifier) > max_lengths["module_identifier"]:
            max_lengths["module_identifier"] = len(module_identifier)
        for current_keyword in all_tables.keys():
            for source_file in source_files:
                try:
                    table_definition = table_definition_parser(os.path.join(args.project, source_file.replace("/", os.path.sep)), current_keyword)
                except IOError:
                    continue
                if len(table_definition) > 0:
                    sys.stderr.write("Found %s definition for '%s' in '%s'\n" % (current_keyword, module_identifier, source_file))
                    all_tables[current_keyword][module_identifier] = table_definition
                    max_len = len(max(table_definition, key=len))
                    if max_len > max_lengths[current_keyword]:
                        max_lengths[current_keyword] = max_len
                    break

    # All preparations done. Lets start parsing the actual log-file.
    sys.stderr.write("\n\n")

    address_maps = {}
    result_names = ["No Match", "Executed", "Delayed", "Guard Failed"]

    events = 0
    results = 0

    def process_s(line):
        address_maps[line[1]] = state_machine_enums.ModuleIdentifier.get_string(int(line[2]))

    def process_i(line):
        module_identifier = address_maps[line[1]]
        global events
        events = events + 1
        print "%s%s\tEvent: %s <- %s" % (
            module_identifier.ljust(max_lengths["module_identifier"], " "),
            "".join(indents[module_identifier]),
            all_tables["STATE_LIST"][module_identifier][int(line[3]) - 1],
            all_tables["EVENT_LIST"][module_identifier][int(line[2])]
        )
        if len(indents[module_identifier]) < 1:
            indents[module_identifier].append("\t")

    def process_r(line):
        module_identifier = address_maps[line[1]]
        global results
        results = results + 1
        if int(line[3]) != 2:
            indents[module_identifier].pop()
        print "%s%s\tResult: %s: %s" % (
            module_identifier.ljust(max_lengths["module_identifier"], " "),
            "".join(indents[module_identifier]),
            all_tables["EVENT_LIST"][module_identifier][int(line[2])],
            result_names[int(line[3])]
        )

    def process_t(line):
        module_identifier = address_maps[line[1]]
        print "%s Transition: %s -> %s" % (
            module_identifier.ljust(max_lengths["module_identifier"], " "),
            all_tables["STATE_LIST"][module_identifier][int(line[2]) - 1],
            all_tables["STATE_LIST"][module_identifier][int(line[3]) - 1]
        )

    process_func = {
        "s": process_s,
        "i": process_i,
        "r": process_r,
        "t": process_t
    }

    for log_file in args.log_file:
        events = 0
        results = 0
        log_file = open(log_file, "r")
        while True:
            line = log_file.readline()
            if not line:
                break

            line = line.strip()
            if line[0] == "&":
                process_func[line[1]](line.split(":"))
            else:
                print line

        log_file.close()
        if events != results:
            print "=============\n Events: %d\nResults: %d" % (events, results)
