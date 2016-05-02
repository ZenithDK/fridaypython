# Parse an output-log with state and event information

## What is it?

This is a script that basically parses everything that's needed in our codebase to resolve
constants for interpreting state- and event information from a debug log to actual names.

## Installation

### On Windows

* Get Python somehow.
  * https://www.google.com/search?q=python+windows

### On a sane operating system

Nothing special should be needed.

## Usage

```bash
python parse.py [-h] [-m MAPPING_FILE] [-p PROJECT] log_file
```
