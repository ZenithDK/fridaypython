#!/usr/bin/env python

import re

line_matches = 0

debug_file = open("input_new.txt", "r")
filetext = debug_file.read()
debug_file.close()

remove_re = re.compile(r"""[^\x20-\x7e\n] |     # Remove all characters outside of [0-9][A-Z][a-z], some special chars, and space
                           <font.*?/font> |     # Remove <font .. /font> blocks
                           On\ char\ channel:\ 0x0\ # Remove 'On char channel: 0x0 ' blocks
                        """, re.DOTALL | re.MULTILINE | re.VERBOSE)
wanted_re = re.compile(r"(\&\#\([^\&]+?\#\&|WARNING:.*?$|INFO:.*?$|ERROR:.*?$)", re.DOTALL | re.MULTILINE)

clean_text = remove_re.sub('', filetext)
matches = re.findall(wanted_re, clean_text)

for match in matches:
    sem_line = match.replace('\n', '')
    line_matches += 1
    print('{}'.format(sem_line))

print('Total matches: {}'.format(line_matches))
