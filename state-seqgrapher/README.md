# Create a UML sequence diagram from state-transition printf's

## What is it?

This is a script that parses a source-file to get state names, and then parses a debug-output logfile to generate
a UML sequence diagram from the state transitions that occurred in the log-file.

Example printf's are in printfs.txt

## Installation

### On Windows

* Get Python somehow.
  * https://www.google.com/search?q=python+windows
* Get seqdiag somehow.
  * https://www.google.com/search?q=python+seqdiag+windows
* Make sure it works together somehow.
  * https://www.google.com/search?q=getting+python+to+work+on+inferior+operating+systems


### On a sane operating system
```bash
$ sudo pip install seqdiag
```

## Usage

```bash
python parse.py <c-file> <log-file>
```
