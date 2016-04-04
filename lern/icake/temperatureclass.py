#!/usr/bin/python3
'''
You decide to test if your oddly-mathematical heating company is fulfilling its All-Time Max, Min, Mean and Mode Temperature Guarantee.

Write a class TempTracker with these methods:

insert() — records a new temperature
get_max() — returns the highest temp we've seen so far
get_min() — returns the lowest temp we've seen so far
get_mean() — returns the mean (average) of all temps so far
get_mode() — returns the mode (which number appears the most times)

For example, in this set:
  [1, 3, 6, 3, 1, 3]
The number 3 appears the most times, so it's the mode.
Careful: a set may have multiple modes.

Optimize for space and time. Favor speeding up the getter functions 
(get_max(), get_min(), get_mean(), and get_mode()) over speeding up 
the insert() function.

get_mean() should return a float, but the rest of the getter 
functions can return integers. Temperatures will all be inserted as 
integers. We'll record our temperatures in Fahrenheit, so we can 
assume they'll all be in the range 0..1100..110.

If there is more than one mode, return any of the modes.
'''

class TempTracker():
  pass


def main():
  pass


if __name__ == '__main__':
  tempObj = TempTracker()
