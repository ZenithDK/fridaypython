# Week 2 - Service Requests locally

## What is it?

Those are two scripts for dealing with the CSR Service Requests database.

One of them crawls the csrsupport.com site for our SR list and then downloads all contents and stores them in a Pickle file.

The other script does a (linear) keyword search through the Pickle file and returns colorized results to STDOUT.

Piping the output to less is useful. An example helper-shellscript is provided.

## Installation

### On Windows

I might add something later.

Basically, you need Python and the following packages:
* colored
* beautifulsoup4
* requests

### On a sane operating system
```bash
$ sudo pip install colored beautifulsoup4 requests
```

## Usage

```bash
python dump.py <username> <password>
```

This will result in a Pickle file called "all.p"

You can then use the search tool to search through the Pickle file:

```bash
python search.py path/to/your/picle/file <searchTerm0> ... [searchTermN]
```

### Example usage:

Creating the dump-file (this is a long and really not that interesting):

[![asciicast](https://asciinema.org/a/29kz3pc5k5uak68dr3iwmjf73.png)](https://asciinema.org/a/29kz3pc5k5uak68dr3iwmjf73)

Perfoming searches:

[![asciicast](https://asciinema.org/a/c7voy1zta7lq422dnutkjp225.png)](https://asciinema.org/a/c7voy1zta7lq422dnutkjp225)
