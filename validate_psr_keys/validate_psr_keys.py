#!/usr/bin/env python

#------------------ Copyright (C) Sennheiser Communications ----------------
# Automated parsing and validation of PS keys used for product configuration
#



import click
import logging
import os
import re
import sys

from collections import OrderedDict

lines_matches = 0
lines_no_matches = 0
lines_ignored = 0

# Keep track of how many bootmode keys we validate
bootmode_keys = 0

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

keys_to_ignore = {
    'f002': 'PSKEY_BLUECORE_TARGET_VARIANT',
    '03cd': 'PSKEY_INITIAL_BOOTMODE',
    '04b0': 'BOOTMODE_KEY_LIST_0',
    '04b1': 'BOOTMODE_KEY_LIST_1',
    '04b2': 'BOOTMODE_KEY_LIST_2',
    '04b3': 'BOOTMODE_KEY_LIST_3',
    '04b4': 'BOOTMODE_KEY_LIST_4',
    '04b5': 'BOOTMODE_KEY_LIST_5',
    '04b6': 'BOOTMODE_KEY_LIST_6',
    '04b7': 'BOOTMODE_KEY_LIST_7',
    '04b8': 'BOOTMODE_KEY_TABLE_0',
    '04f8': 'BOOTMODE_KEY_TABLE_1',
    '0538': 'BOOTMODE_KEY_TABLE_2',
    '0578': 'BOOTMODE_KEY_TABLE_3',
    '05b8': 'BOOTMODE_KEY_TABLE_4',
    '05f8': 'BOOTMODE_KEY_TABLE_5',
    '0638': 'BOOTMODE_KEY_TABLE_6',
    '0678': 'BOOTMODE_KEY_TABLE_7',
}

# Instead of validating each PS key the BOOTMODE_KEY_TABLE_X's refer to, assume everything between
# BOOTMODE_KEY_TABLE_1, BOOTMODE_KEY_TABLE_1 + BOOTMODE_KEY_TABLE_RANGE
# to be valid
BOOTMODE_KEY_TABLE_RANGE = 8*64

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-d', '--debug', is_flag=True)
@click.option('-q', '--quiet', is_flag=True)
@click.argument('secom_psr_file',
                type=click.File('rb'),
                required=True)
@click.argument('csr_psr_txt',
                type=click.File('rb'),
                required=True)
def main(secom_psr_file, csr_psr_txt, debug, quiet):
    global lines_matches, lines_no_matches, lines_ignored, bootmode_keys

    # Initialize logging
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.DEBUG if debug else logging.ERROR if quiet else logging.INFO)

    secom_psr_contents = secom_psr_file.read()
    csr_psr_contents = csr_psr_txt.read()

    secom_psr_keys = re.compile(r"^\&([0-9a-zA-Z]{4})", re.MULTILINE)
    csr_psr_keys = re.compile(r"""^NAME[\s\r\n]+        # Match the NAME and spaces/newlines after
                                  (PSKEY_[A-Z0-9\_]*)\s    # Match the name of the PSKEY
                                  \(0x([0-9a-zA-Z]{4})  # Match the key of the PS key
                               """, re.VERBOSE | re.MULTILINE | re.DOTALL)

    # Find all matches of CSR and SECOM PS keys
    secom_psr_matches = re.findall(secom_psr_keys, secom_psr_contents)
    csr_psr_matches = re.findall(csr_psr_keys, csr_psr_contents)
    # Findall for the psrkeys.txt returns a list of tuples on the form of (PSKEY_XXX, 0000)
    # We want them in the other form (0000, PSKEY_XXX), so swap them around
    csr_psr_matches = [(b, a) for a, b in csr_psr_matches]

    csr_psr_dict = dict(csr_psr_matches)

    # Find all PS keys used for setting bootmodes and make sure the PS keys they are referencing are correct as well
    bootmode_key_list = [key for key in sorted(keys_to_ignore.iterkeys()) if 'BOOTMODE_KEY_LIST' in keys_to_ignore[key]]
    for ps_key in bootmode_key_list:
        bootmode_key_count = 0
        # Create custom regex for each PSKEY_BOOTMODE_KEY_LIST_X key used
        regex_string = r"^\&{ps_key} = ((?:[0-9a-zA-Z]{{4}}| )*)".format(ps_key=ps_key)
        bootmode_key_match = re.compile(regex_string, re.MULTILINE)
        bootmode_key_list_keys = re.findall(bootmode_key_match, secom_psr_contents)

        # Only iterate over the PS keys used in the PSKEY_BOOTMODE_KEY_LIST_X key if there are some
        if len(bootmode_key_list_keys) > 0:
            bootmode_key_count = len(bootmode_key_list_keys[0].split(' '))
        logging.info('Validating {} - #{} keys: {}'.format(keys_to_ignore[ps_key], bootmode_key_count, ''.join(bootmode_key_list_keys)))
        if bootmode_key_count > 0:
            for bootmode_key_item in bootmode_key_list_keys[0].split(' '):
                bootmode_keys += 1
                if bootmode_key_item in csr_psr_dict:
                    logging.debug('{} contains valid key, ignore: {}'.format(keys_to_ignore[ps_key], bootmode_key_item))
                    lines_ignored += 1
                else:
                    logging.error('{} contains invalid key: {}'.format(keys_to_ignore[ps_key], bootmode_key_item))
                    lines_no_matches += 1


    logging.info('CSR keys found: {} - PS keys found in provided file (bootmodes and regular PS keys): {}'.format(len(csr_psr_matches), len(secom_psr_matches) + bootmode_keys))

    for ps_key in secom_psr_matches:
        if ps_key in keys_to_ignore:
            logging.info('Found key "{} ({})" in list of PS keys to ignore'.format(ps_key, keys_to_ignore[ps_key]))
            lines_ignored += 1
        elif ps_key in csr_psr_dict:
            logging.debug('Found key "{} ({})" in CSR PS keys'.format(ps_key, csr_psr_dict[ps_key]))
            lines_matches += 1
        elif int(ps_key, 16) >= int('04b8', 16) and int(ps_key, 16) < int('04b8', 16) + BOOTMODE_KEY_TABLE_RANGE:
            bootmode_key_table_offset = (int(ps_key, 16) - 1208) / 64
            bootmode_key_table_index = '{:02x}'.format(0x04b8 + bootmode_key_table_offset * 64).zfill(4)
            logging.info('Found unknown key "{}" within the range of {}+[0-64], ignore'.format(ps_key, keys_to_ignore[bootmode_key_table_index]))
            lines_ignored += 1
        else:
            logging.error('Found key that is NOT in CSR PS keys: "{}"'.format(ps_key))
            lines_no_matches += 1

    logging.info('PS keys that could be found in {}: {}'.format(os.path.basename(csr_psr_txt.name), lines_matches))
    logging.info('PS keys that were ignored: {}'.format(lines_ignored))
    logging.info('PS keys that had NO matches: {}'.format(lines_no_matches))

    if lines_no_matches > 0:
        sys.exit(-1)


if __name__ == '__main__':
    main()
