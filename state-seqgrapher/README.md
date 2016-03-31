# Create a UML sequence diagram from state-transition printf's

## What is it?

This is a script that parses a source-file to get state names, and then parses a debug-output logfile to generate
a UML sequence diagram from the state transitions that occurred in the log-file.

Example printf's are in printfs.txt

## Installation

### On Windows

I might add something later. Or not.

### On a sane operating system
```bash
$ sudo pip install seqdiag
```

## Usage

```bash
python parse.py <c-file> <log-file>
```
