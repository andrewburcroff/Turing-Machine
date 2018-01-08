Andrew Burcroff
Benjamin A. Slack
CS5800
Project: Turing Machine Simulator

Abstract:
For this project, we intend to create a simulator for a standard 
Turing Machine using Python 3.6.1. The Turing Machine (TM) will be
programmed via a text input format of our own devising.

User Guide:
First, please note. We developed this project using Python 3.6.1.
The machine package makes extensive use of the new type hinting
introduced in Python 3.6. It will not run under earlier versions of
Python. You can use pyenv to compile and install Python 3.6 if your
testing system python version is not up to date. More info on that
procedure is available here:

https://github.com/pyenv/pyenv

simulator.py (Ben)

Usage:
python3 simulator.py -i <your input> -t <filepath> [-d]
-i: string to be placed on the machine tape. The TMTape class
    automatically adds blanks to the start and end.
-t: the location of the configuration file to load. Configuration
    files are JSON formatted text files consisting of the
    specification of their respect turing machine.
-d: dump the configuration of the machine. This outputs the JSON
    configuration of the loaded machine after executing. It’s
    offered as a convenience method.
