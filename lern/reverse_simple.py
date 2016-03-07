#!/usr/bin/python3
'''
some ways to reverse a string or list
'''
stringy = 'potato'
[stringy[-i] for i in range(1,len(stringy)+1)]
# the -1 on the end of range tells it to count backwards
[stringy[i] for i in range(-1,-len(stringy),-1)]

def recurse(stringy):
  if len(stringy) >= 1:
    print(stringy[-1],end='')
    recurse(stringy[:-1])
  else:
    return True
recurse('blah strawberry')

listy = list(stringy)
listy.reverse()
''.join(listy)
