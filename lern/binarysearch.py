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
