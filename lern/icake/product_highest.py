#!/usr/bin/python3
'''
Given a list_of_ints, find the highest_product you can get
from three of the integers.

The input list_of_ints will always have at least three integers.

Does your function work with negative numbers? eg:

  [-10,-10,1,3,2]  == 300. -10*-10*3


'''

def highest_product(intlist):
  # This doesn't work for negative numbers
  #highestnums = sorted(intlist, reverse=True)
  #print(highestnums[0] * highestnums[1] * highestnums[2])



if __name__ == '__main__':
  highest_product([1,3,4,2,40,6])  # 960
  highest_product([-10,-10,1,3,2])  # 300
