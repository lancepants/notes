#!/usr/bin/python3
'''
Given a list_of_ints, find the highest_product you can get
from three of the integers.

The input list_of_ints will always have at least three integers.

Does your function work with negative numbers? eg:

  [-10,-10,1,3,2]  == 300. -10*-10*3


'''

def highest_product_brute(intlist):
  # This doesn't work for negative numbers
  #highestnums = sorted(intlist, reverse=True)
  #print(highestnums[0] * highestnums[1] * highestnums[2])

  # Here is the brute force method. Create a permutation list. 
  # 0(n^3) , works with negative numbers
  # Multiply every number by two other numbers. Create new 
  # lists so as not to multiply a number by itself
  products = []
  for n in intlist:
    intlist_inner1 = intlist[:]
    intlist_inner1.remove(n)
    for n_inner1 in intlist_inner1:
      intlist_inner2 = intlist_inner1[:]
      intlist_inner2.remove(n_inner1)
      for n_inner2 in intlist_inner2:
        products.append(n*n_inner1*n_inner2)
  print(max(products))

def highest_product_icake(intlist):
  '''
  This question can be solved in O(n) time...
  '''
  highest_product = 0
  pass


if __name__ == '__main__':
  highest_product([1,3,4,2,40,6])  # 960
  highest_product([-10,-10,1,3,2])  # 300
