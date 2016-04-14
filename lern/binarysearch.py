#!/usr/bin/env python
'''
The recursion solutions here rely on searching some global variable outside
of their scope. The alternative to this is to continually pass a new smaller
list up, but that is very space inefficient.

'''
import sys
import random

rnum = random.randint(1,1000)

def guessloop(nmin,nmax):
    print "Guess a number from %d to %d :" % (nmin, nmax)
    guess = int(raw_input())
    verify(guess,nmin,nmax)

def verify(guess,nmin,nmax):
    if guess == rnum:
        print "Correct! Number was %d" % rnum
        exit()
    elif guess > rnum:
        print "Too high. Readjusting constraints."
        nmax = guess - 1
        guessloop(nmin,nmax)
    elif guess < rnum:
        print "Too low. Readjusting constraints."
        nmin = guess + 1
        guessloop(nmin,nmax)

if __name__ == '__main__':
    nmin = 1
    nmax = 1000
    guessloop(nmin,nmax)


'''
Alternately, without input
'''
#!/usr/bin/python3
import random
randnum = random.randint(1,1000)
print("randnum is " + str(randnum))
def recurse(tries, guess, minval, maxval):
  print(guess)
  if guess == randnum:
    print("Number is " + str(guess))
    print("It took " + str(tries) + " guesses.")
    return guess
  elif guess > randnum:
    tries += 1
    maxval = guess-1
    guess = minval + ((maxval - minval)/2)
    recurse(tries,int(guess),minval,maxval)
  elif guess < randnum:
    tries += 1
    minval = guess+1
    guess = minval + ((maxval - minval)/2)
    recurse(tries,int(guess),minval,maxval)

'''
Alternately, not using recursion
'''
def binsearch(lookfor, listy):
  middle = int((len(listy)-1)/2)
  print(middle)
  first = 0
  last = len(listy)-1
  itercatch = 0
  while True:
    # reset middle to first plus half of the new index range
    middle = int((last - first)/2) + first
    print('middle is now {}'.format(middle))
    if itercatch > 2:
      return False
    if listy[middle] == lookfor:
      print(middle)
      return middle
    elif listy[middle] > lookfor:
      print('{} is greater than {}'.format(listy[middle], lookfor))
      last = middle - 1
      itercatch += 1
    elif listy[middle] < lookfor:
      print('{} is less than {}'.format(listy[middle], lookfor))
      first = middle + 1
      itercatch += 1

if __name__ == '__main__':
  binsearch(38, [2,7,12,13,19,27,38,99,102])
  recurse(1,500,1,1000)
  #guessloop()  # interactive

