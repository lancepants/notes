#!/usr/bin/python3
'''
You have a list of integers, and for each index you want to 
find the product of every integer except the integer at that 
index. 
Write a function get_products_of_all_ints_except_at_index() 
that takes a list of integers and returns a list of the 
products.

For example, given:
  [1, 7, 3, 4]

your function would return:
  [84, 12, 28, 21]

by calculating:
  [7*3*4, 1*3*4, 1*7*4, 1*7*3]

Do not use division in your solution.
'''

def get_products_brute(intlist):
  '''
  brute force O(n^2)
  go through each, make new list with other nums excluded
  '''
  products = []
  for n in intlist:
    product = 1
    inner_nums = intlist[:]
    inner_nums.remove(n)
    for inner_n in inner_nums:
      product = product * inner_n
    products.append(product)
  print(products)

def get_products_icake(intlist):
  '''
  Try for O(n). icake answer
  '''
  # Generate a list filled with 'None' for each index
  products_before_index = [None] * len(intlist)
  product_so_far = 1
  # Generate a list of products of all integers before the index
  for i in range(len(intlist)):
    products_before_index[i] = product_so_far
    product_so_far *= intlist[i]

  # Generate a list of products of all integers after the index
  products_after_index = [None] * len(intlist)
  product_so_far = 1
  # avoid reversing the list, doing the same as above, then
  # reversing the result. Do this by running through indexes
  # in reverse
  i = len(intlist) - 1
  while i >= 0:
    products_after_index[i] = product_so_far
    product_so_far *= intlist[i]
    i -= 1

  # Now multiply each ele of the two lists together. Note
  # we could do this step above, in our while loop,  without 
  # needing to create a third list.
  finallist = []
  for i in range(len(intlist)):
    finallist.append(products_before_index[i] * products_after_index[i])

  print(finallist)
    


if __name__ == '__main__':
  get_products_brute([1,7,3,4])
  get_products_brute([1,1,1,0])
  get_products_icake([1,7,3,4])
  get_products_icake([1,1,1,0])
