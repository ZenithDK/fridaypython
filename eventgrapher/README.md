# Event Grapher

## What is it?

This is a diagram-generator for application/config/vmkit/\*\_config.h files that contan event-tables.

This script depends on Graphviz, i.e. both the executables and the Python package.

## Installation

### On Windows
* Install graphviz using the Windows MSI package from http://www.graphviz.org/Download_windows.php or the one from this repository (Graphviz.org is down at the time this is written).
* Extract the graphviz-0.4.10-jofr.zip file from this repository somewhere to your computer and open up a terminal.

Assuming you have Python installed and in your path:

```cmd
 > cd to\where\you\extracted\the\archive
 > python setup.py install
```

This version of the graphviz Python library has some of my own fixes that makes it compatible with the latest version of Graphviz.

### On a sane operating system
```bash
$ sudo apt-get install graphviz
$ sudo pip install graphviz
```

## Usage

```bash
python eventgrapher.py <name_of_config_file>
```

The output will be saved to \<basename\_of\_config\_file\>.svg

I have decided not to provide an example output here since this is a public repository.
