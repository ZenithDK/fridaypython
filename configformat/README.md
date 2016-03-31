# Config Format

## What is it?

This is a formatter for application/config/vmkit/\*\_config.h files.

It does two things:

* Formats the state- and event-tables to an even column width
* If a \<state\> not equal to "0" and \<new state\> is the same as \<state\>, then \<new state\> is replaced with "0".

## Usage

This script just prints the results to STDOUT, so you probably want to redirect the output to a file.

```bash
python format.py name-of-config-file.h > new.h
```

You should then do a diff of the original file and new.h to make sure everything is OK. I don't trust this script to change stuff without supervision yet!

If everything seems ok, replace the original one with new.h

In the future, when I have gained enough trust in this code, I might add an option to edit the file in-place.
