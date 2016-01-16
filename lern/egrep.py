#!/usr/bin/env python
'''
A very basic python egrep
ToDo:
-Add support for 'multiple|patterns'
'''
import re
import sys

def main(pattern, filetosearch):
    with open(filetosearch) as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                print line,
        f.close()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
