#!/usr/bin/python3
'''
Takes a text file as input. Outputs a count of how many times each
word appears in the text.
Todo:
    Filter out syntax
    lower-case everything
'''
import sys
def freqgen(wlist):
    dicky = {}
    for w in wlist:
        try:
            dicky[w] = dicky[w] + 1
        except KeyError:
            dicky[w] = 1
    # Let's convert the dict to a list of tuples (dicky.items()) 
    # for easier sorting. Key off the second value in each tuple
    for k, v in sorted(dicky.items(), key=lambda x: x[1]):
        print(k + " " + str(v))

if __name__ == '__main__':
    with open(sys.argv[1], "r") as f:
        bigstring = f.read().replace("\n", " ")
        wlist = bigstring.split()
    freqgen(wlist)

