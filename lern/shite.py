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
