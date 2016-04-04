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
  def __init__(self):
    self.temps = []

  def insert(self, newtemps):
    for n in newtemps:
      self.temps.append(n)

  def get_max(self):
    # max is O(n)
    return max(self.temps)

  def get_min(self):
    # min is O(n)
    return min(self.temps)

  def get_mean(self):
    total = 0
    for n in self.temps:
      total += n
    # Result of division in python is already a float
    avg = total/len(self.temps)
    return avg

  def get_mode(self):
    d = {k:0 for k in set(self.temps)}
    for n in self.temps:
      d[n] += 1

    # We can do an O(n log n) or O(n) at best, but we have to
    # duplicate the data to a new obj to do so.
    #sortedvals = sorted(d.items(), key=lambda x: x[1], reverse=True)

    # Instead, we can do an O(n) walk through and just keep track of 
    # the highest value we've seen so far, and the key (temperature)
    highest = 0
    key = 0
    for k,v in d.items():
      if v > highest:
        highest = v
        key = k
    return key


if __name__ == '__main__':
  tempObj = TempTracker()
  tempObj.insert([4,6,1,9,8,8,4,8])
  print(tempObj.temps)
  print(tempObj.get_max())
  print(tempObj.get_min())
  print(tempObj.get_mean())
  print(tempObj.get_mode())
