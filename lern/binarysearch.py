#!/usr/bin/env python
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

if __name__ == '__main__':
  recurse(1,500,1,1000)

