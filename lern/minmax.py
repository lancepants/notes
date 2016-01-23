#!/usr/bin/python3
'''
Re-implement the min() and max() functions. Min and Max accept both
an iterator, or two or more arguments. They also accept an optional
key= function, that is used to extract a comparison key from each
list element (eg: key=str.lower).

So, you'll need to have several functions:
    max(iterable, *[, key])
    min(iterable, *[, key])
    max(arg1, arg2, *args[, key])
    min(arg1, arg2, *args[, key])
'''
def max(iterable, key=None):
  curmax=iterable[0]
  print(iterable)
  if key:
    dicky = {}
    # Generate a dict where dict key is keyfn(iteritem) and
    # dict key value is the input list index location
    for index in range(len(iterable)):
      dicky[key(iterable[index])] = index
    for i in dicky:
      if i > curmax:
        curmax = i
    print(iterable[dicky[curmax]])
    return iterable[dicky[curmax]]
  else:
    for i in iterable:
      if i > curmax:
          curmax = i
  print(curmax)
  return curmax

def min(iterable, key=None):
  curmin=iterable[0]
  print(iterable)
  if key:
    dicky = {}
    # Generate a dict where dict key is keyfn(iteritem) and
    # dict key value is the input list index location
    for index in range(len(iterable)):
      dicky[key(iterable[index])] = index
    for i in dicky:
      if i < curmin:
        curmin = i
    print(iterable[dicky[curmin]])
    return iterable[dicky[curmin]]
  else:
    for i in iterable:
      if i < curmin:
          curmin = i
  print(curmin)
  return curmin


if __name__ == '__main__':
  max([1,2,3])
  max([1,2,4,3,4], key=lambda x: x**2)
  min([1,2,3])
  min([1,2,4,3,4], key=lambda x: x**2)
#  max(3, 2)
#  min(3, 2)
  max([1, 2, 0, 3, 4])
  min("hello")
#  max(2.2, 5.6, 5.9, key=int)
  min([[1,2], [3, 4], [9, 0]], key=lambda x: x[1])

'''
max(3, 2) == 3
min(3, 2) == 2
max([1, 2, 0, 3, 4]) == 4
min("hello") == "e"
max(2.2, 5.6, 5.9, key=int) == 5.6
min([[1,2], [3, 4], [9, 0]], key=lambda x: x[1]) == [9, 0]
'''
