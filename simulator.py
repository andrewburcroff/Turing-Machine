import os
import machine
import sys

kTOK_TM = "-t"
kTOK_INPUT = "-i"
kTOK_DUMP = "-d"
kUNIXSEP = "/"
kWINSEP = "\\"
kMACSEP = ":"

def pathfix(rawpath: str)->os.path:
    if kUNIXSEP in rawpath:
        parts = rawpath.split(kUNIXSEP)
    elif kWINSEP in rawpath:
        parts = rawpath.split(kWINSEP)
    else:
        parts = rawpath.split(kMACSEP)
    first = parts.pop(0)
    return os.path.join(os.path.expanduser(first), *parts)

if __name__ == "__main__":
    filepath = None
    w = None
    dump = False
    execute = False
    #parse command line
    for i in range(len(sys.argv)):
        if sys.argv[i] == kTOK_TM:
            filepath = pathfix(sys.argv[i+1])
        if sys.argv[i] == kTOK_INPUT:
            w = sys.argv[i+1]
            execute = True
        if sys.argv[i] == kTOK_DUMP:
            dump = True
    #load a machine
    M = machine.TM(filepath)
    #if there's input output the trace
    if execute:
        T = machine.TMTape(w)
        M.load(T)
        trace = M.exec()
        for item in trace:
            print(item)
    #if a dump of the config is requested output that
    if dump:
        print(M.dumps())
    exit(0)