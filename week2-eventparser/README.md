# Week 2 - Event Parser

## What is it?

This is a diagram-generator for application/config/vmkit/\*\_config.h files that contan event-tables.

This script depends on Graphviz, i.e. both the executables and the Python package.

## Installation
```bash
$ sudo apt-get install graphviz
$ sudo pip install graphviz
```

## Usage

```bash
python eventparser.py <name_of_config_file>
```

The output will be saved to <basename\_of\_config\_file>.sd.pdf

I have decided not to provide an example output here since this is a public repository.
