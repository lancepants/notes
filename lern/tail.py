#!/usr/bin/env python
'''
This is imperfect as start printing from 100B is pretty arbitrary.
Unfortunately there is no efficient way to tell it to go back a certain
number of lines, as that would require reading the entire file and
parsing each char for a newline char and building an index.
'''
import time
import sys

def main(f):
  # Go to end of file
  f.seek(0, 2)
  # Start printing from EOF minus 100 chars. If file not 100chars, start printing from beginning
  pos = f.tell() - 100
  if pos < 0:
    f.seek(0)
  else:
    f.seek(pos)
    # Using readline() and silencing output will cheaply get our file position pointer to the next
    # line without printing a truncated line to the user (as a result of seeking back an arbitrary
    # 100chars)
    silence = f.readline()
  while True:
    # readline() reads a line and then advances the position read/write pointer on the file object
    line = f.readline()
    # If readline doesn't return anything, sleep for a second
    # Not sure exactly why the seek to prev pos is needed. Sometimes readline sucks?
    if not line:
      time.sleep(1)
    else:
      print line,

if __name__ == '__main__':
  main(open(sys.argv[1]))
