import machine
import re
import os
import sys

if __name__ == "__main__":
    print("Please input a valid path name? Path name must be in this format: /home/Documents/....../file.tm")
    path = input("Enter:")
    #This line is for testing: "/home/brandon/Documents/5800/CS5800-proj/configs/ex_821.tm"
    if os.path.isfile(path) and os.access(path, os.R_OK):
        tm = machine.TM(path)
        value = input("Please input the tape you want to use?")
        valuelist = list(value)
        fox = tm.alpha
        if (fox.issubset(valuelist)):
            mytape = machine.TMTape(valuelist)
            try:
                tm.load(mytape)
                for config in tm.exec():
                    print(config)
                    if 'Rejected:' in config:
                        print("The input: " + value + " entered did NOT the final state. The final state:")
                        print(tm.accept)

                    elif 'Accepted:' in config:
                        print("Congratulations: " + value + " was ACCEPTED.")
            except machine.InvalidCharacterInTape as e:
                print(type(e), *e.args)

        else:
            print("The entered tape is not a subset of the Language:")
            print(tm.tapealpha)

    else:
        print("BAD PATHFILE")
pass