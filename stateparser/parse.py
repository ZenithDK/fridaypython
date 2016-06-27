#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import coloredlogs
import click
import ConfigParser
import fileinput
import logging
import re
import os
import sys

from utils import enum_parser, table_definition_parser

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

events = 0
results = 0

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-r", "--raw", is_flag=True)
@click.option("-d", "--debug", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
@click.option("-m", "--mapping",
              type=click.File('rb'),
              required=False,
              help="File containing mappings between enums and header-files",
              default="default_mappings.ini")
@click.option("-p", "--project", "project",
              type=click.Path(file_okay=False),
              help="Specify project folder",
              default=".")
@click.argument("input_file",
                type=click.Path(allow_dash=True, dir_okay=False))
def main(raw, debug, verbose, input_file, project, mapping):
    # Initialize logging
    #logging.basicConfig(format='{}%(levelname)s %(message)s'.format('%(asctime)s ' if verbose and not raw else ''),
    #                    datefmt='%Y-%m-%d %H:%M:%S',
    #                    level=logging.DEBUG if debug else logging.INFO)

    # Initialize coloredlogs
    coloredlogs.install(fmt="{}%(message)s".format("%(asctime)s %(levelname)s " if verbose and not raw else ""),
                        level=logging.DEBUG if debug else logging.INFO)

    mappings = ConfigParser.ConfigParser()

    try:
        mappings.readfp(mapping)
    except IOError as e:
        logging.error("Error: Could not open: {}".format(e.filename))
        sys.exit(1)

    if not mappings.has_section('mappings'):
        logging.error("Error: Could not find a 'mappings' section in '{}'".format(mapping))
        sys.exit(1)

    try:
        state_machine_enums = enum_parser(os.path.join(
            project,
            "vmkit",
            "src",
            "secom",
            "state_machine",
            "state_machine.h"
        ))
        getattr(state_machine_enums, 'ModuleIdentifier')
    except IOError as e:
        logging.error("Error: Could not open: {}".format(e.filename))
        sys.exit(1)
    except AttributeError:
        logging.error("Error: 'state_machine.h' does not contain an enum for 'ModuleIdentifier'")
        sys.exit(1)

    all_tables = {'STATE_LIST' : {}, 'EVENT_LIST' : {} }
    max_lengths = {'STATE_LIST' : 0, 'EVENT_LIST' : 0, 'module_identifier' : 0}
    indents = {}

    for module_identifier in state_machine_enums.ModuleIdentifier.get_all_strings():
        source_files = ast.literal_eval(mappings.get('mappings', module_identifier))
        indents[module_identifier] = []
        if len(module_identifier) > max_lengths["module_identifier"]:
            max_lengths["module_identifier"] = len(module_identifier)
        for current_keyword in all_tables.keys():
            for source_file in source_files:
                try:
                    table_definition = table_definition_parser(os.path.join(project, source_file.replace("/", os.path.sep)), current_keyword)
                except IOError:
                    continue
                if len(table_definition) > 0:
                    logging.debug("Found {} definition for {} in {}".format(current_keyword, module_identifier, source_file))
                    all_tables[current_keyword][module_identifier] = table_definition
                    max_len = len(max(table_definition, key=len))
                    if max_len > max_lengths[current_keyword]:
                        max_lengths[current_keyword] = max_len
                    break

    # All preparations done. Lets start parsing the actual log-file.
    address_maps = {}
    result_names = ["No Match", "Executed", "Delayed", "Guard Failed" ]

    def process_state(param_list):
        address_maps[param_list[1]] = state_machine_enums.ModuleIdentifier.get_string(int(param_list[2]))
        #logging.info('SS-DUDE: {} = {}'.format(param_list, address_maps[param_list[1]]))

    def process_event(param_list):
        global events
        module_identifier = address_maps[param_list[1]]
        events = events + 1
        logging.info("{}{}\tEvent: {} <- {}".format(
            module_identifier.ljust(max_lengths["module_identifier"], " "),
            "".join(indents[module_identifier]),
            all_tables["STATE_LIST"][module_identifier][int(param_list[3])-1],
            all_tables["EVENT_LIST"][module_identifier][int(param_list[2])]
        ))
        if len(indents[module_identifier]) < 1:
            indents[module_identifier].append("\t")

    def process_result(param_list):
        global results
        module_identifier = address_maps[param_list[1]]
        results = results + 1
        if int(param_list[3]) != 2:
            indents[module_identifier].pop()
        logging.info("{}{}\tResult: {}: {}".format(
            module_identifier.ljust(max_lengths['module_identifier'], ' '),
            ''.join(indents[module_identifier]),
            all_tables['EVENT_LIST'][module_identifier][int(param_list[2])],
            result_names[int(param_list[3])]
        ))

    def process_transition(param_list):
        module_identifier = address_maps[param_list[1]]
        logging.info("{} Transition: {} -> {}".format(
            module_identifier.ljust(max_lengths['module_identifier'], ' '),
            all_tables['STATE_LIST'][module_identifier][int(param_list[2])-1],
            all_tables['STATE_LIST'][module_identifier][int(param_list[3])-1]
        ))

    process_func = {
        's' : process_state,
        'i' : process_event,
        'r' : process_result,
        't' : process_transition
    }

    print_keywords = {
        'WARN:' : logging.warn,
        'INFO:' : logging.info,
        'ERROR' : logging.error
    }

    partial_match = ''
    remove_re = re.compile(r"""[^\x20-\x7e\n] |     # Remove all characters NOT [0-9][A-Z][a-z], some special chars, and space
                               <font.*?/font> |     # Remove <font .. /font> blocks
                               On\ char\ channel:\ 0x0\ # Remove 'On char channel: 0x0 ' blocks
                            """, re.DOTALL | re.MULTILINE | re.VERBOSE)
    wanted_re = re.compile(r"(\&\#\([^\&]+?\#\&|WARNING:.*?$|INFO:.*?$|ERROR:.*?$)", re.DOTALL | re.MULTILINE)

    file = fileinput.input(files=(input_file))

    for line in file:
        clean_text = remove_re.sub('', line)

        if len(partial_match) != 0:
            #print('=== Prepending partial_match ***{}*** to clean_text ***{}***'.format(partial_match, clean_text))
            clean_text = partial_match + clean_text
            partial_match = ''

        if clean_text.count('&#') != clean_text.count('#&'):
            partial_match = clean_text
            #print('=== Partial_match ***{}***, saving for next pass'.format(partial_match))
        else:
            #print('=== Haystack ***{}***'.format(clean_text))
            matches = re.findall(wanted_re, clean_text)

            for match in matches:
                if match[:5] in print_keywords.keys():
                    print_keywords[match[:5]](match)
                elif match[:3] == '&#(':
                    sem_line = match.replace('\n', '')
                    if raw:
                        logging.info(sem_line)
                    else:
                        sem_line = re.sub('&#\(|\)#&', '', sem_line)
                        args = sem_line.split(":")

                        #if args[0] == 's':
                            #logging.info('STATE: {} - args: {} - maps_size: {}'.format(sem_line, args, len(address_maps)))
                        #    process_func[sem_line[0]](args)
                        if args[0] == 's' or args[1] in address_maps:
                            #logging.info('PROCESS_NOT_S: {} - args: {} - maps_size: {}'.format(sem_line, args, len(address_maps)))
                            process_func[sem_line[0]](args)
                        else:
                            logging.error("Cannot {} as we never parsed a state transition first - {}".format(' '.join(process_func[sem_line[0]].__name__.split('_')), sem_line))
                else:
                    logging.info("??: {} || {}".format('\\x'.join(x.encode('hex') for x in line), line))

    if events != results:
        logging.info("=============\n Events: {}\nResults: {}".format(events, results))


if __name__ == "__main__":
    main()
