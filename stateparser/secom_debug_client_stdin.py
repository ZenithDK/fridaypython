#!/usr/bin/env python

import re
import sys

remove_re = re.compile(r"""[^\x20-\x7e\n] |     # Remove all characters outside of [0-9][A-Z][a-z], some special chars, and space
                           <font.*?/font> |     # Remove <font .. /font> blocks
                           On\ char\ channel:\ 0x0\ # Remove 'On char channel: 0x0 ' blocks
                        """, re.DOTALL | re.MULTILINE | re.VERBOSE)
wanted_re = re.compile(r"(\&\#\([^\&]+?\#\&|WARNING:.*?$|INFO:.*?$|ERROR:.*?$)", re.DOTALL | re.MULTILINE)

line_matches = 0

partial_match = ''

for text in sys.stdin:
    clean_text = remove_re.sub('', text)

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
            sem_line = match.replace('\n', '')
            line_matches += 1
            print('{}'.format(sem_line))

print('Total matches: {}'.format(line_matches))
