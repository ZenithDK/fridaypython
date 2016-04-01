# Tools for dealing with PSKeys documentation

## What is it?

Those are three scripts:

### parsekeys.py

This is a script that parses pskeys.txt (from the ADKs) and id_userkey.h (from flashMan) and creates
a Python pickle file and merges the data from those two files together.

### dumpkeys.py

This script reads in the pickle file and dumps all contents in a human-readable format to STDOUT.
The output can be piped to a file, thus creating a new file equivalent to pskeys.txt but with
SECOM information added.

### searchkeys.py

This script uses the pickle file and does a text-search through it. It returns all PSKey-entries where any
of the fields match the search criteria, in a nice VT100 colored format.

## Installation

### On Windows

* Get Python somehow.
  * https://www.google.com/search?q=python+windows
* Get colored somehow.
  * https://www.google.com/search?q=python+colored+windows
* Make sure it works together somehow.
  * https://www.google.com/search?q=getting+python+to+work+on+inferior+operating+systems


### On a sane operating system
```bash
$ sudo pip install colored
```

## Usage

```bash
python parsekeys.py <pskeys.txt> <id_userkey.h>
```

```bash
python dumpkeys.py > somename.txt
```

```bash
python searchkeys.py <searchString1> ... [searchStringN]
```

