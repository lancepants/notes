#!/usr/bin/python3
'''
print readable chars.

content = f.read() # reads entire file into memory
content = f.readlines() # reads entire file into memory, one list ele per line
oneline = f.readline() # generator. Reads a single line, moves file ptr
f.pos(0,2) # set ptr to end of file
f.seek(0) # set ptr to defined position. 0=start of file
f.tell() # get current ptr pos
ptr's go up one char at a time. 0 = first char, 1 = second char, ...
'''
with open('api-examples', 'r') as f:
  for line in f.readline():
    for c in line:
      if c.isalpha():
        print(c, sep='', end='')  # end='' means don't print newline
  print('\n')


'''
dict stuff
'''
listofkeys = ['potato','basketball','derptastic','potato']
d = {k:0 for k in listofkeys}

if somekey in d:
  d[somekey] += 1
else:
  d[somekey] = 0



