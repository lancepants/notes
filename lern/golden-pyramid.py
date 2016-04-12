#!/usr/bin/python3
'''
http://www.checkio.org/mission/golden-pyramid/

Our Robo-Trio need to train for future journeys and treasure hunts. Stephan has
built a special flat model of a pyramid. Now the robots can train for speed
gold running. They start at the top of the pyramid and must collect gold in
each room, choose to take the left or right path and continue down to the next
level. To optimise their gold runs, Stephan need to know the maximum amount of
gold that can be collected in one run.

Consider a tuple of tuples in which the first tuple has one integer and each
consecutive tuple has one more integer then the last. Such a tuple of tuples
would look like a triangle. You should write a program that will help Stephan
find the highest possible sum on the most profitable route down the pyramid.
All routes down the pyramid involve stepping down and to the left or down and
to the right.

Tips: Think of each step down to the left as moving to the same index location
or to the right as one index location higher. Be very careful if you plan to
use recursion here.

Input: A pyramid as a tuple of tuples. Each tuple contains integers.

Output: The maximum possible sum as an integer.

Example:

count_gold((
    (1,),
    (2, 3),
    (3, 3, 1),
    (3, 1, 5, 4),
    (3, 1, 3, 1, 3),
    (2, 2, 2, 2, 2, 2),
    (5, 6, 4, 5, 6, 4, 3)
)) == 23
count_gold((
    (1,),
    (2, 1),
    (1, 2, 1),
    (1, 2, 1, 1),
    (1, 2, 1, 1, 1),
    (1, 2, 1, 1, 1, 1),
    (1, 2, 1, 1, 1, 1, 9)
)) == 15
count_gold((
    (9,),
    (2, 2),
    (3, 3, 3),
    (4, 4, 4, 4)
)) == 18



- calculate all possible paths
  - extrapolate maximum number of paths by counting at each depth,
    looking for a pattern

1 2 4 8 16 32 64  # max paths
0 1 2 3 4  5  6   # tree depth (starts at 0, root node=0)

- Looks like 2^tree_depth = maxpaths.
  - tree_depth = len(last_ele)-1 or len(input_list)-1
- if remain at same index is 0, and go down and right is 1, then
  all available paths are a combination of 0 and 1 in len(maxpaths)
'''

import itertools
def count_gold(tuplist):
  depth = len(tuplist)
  maxpaths = 2**depth - 1

  # itertools.product will return all possible combo's of  given elements,
  # within a length given (repeat). Normally returns an iter object that
  # returns tuples, so we use list comprehension here to generate a list
  # of lists.
  combos = [list(c) for c in itertools.product([0, 1], repeat=depth)]
  print(combos)

  '''
  currently erroring because final [1,1,1,1] combo tries to get tuple[0][1]
  when it does not exist (first ele of first tuple has len=1)
  '''
  for combo in combos:
    starting_element = 0
    tup_element = 0
    product = 0
    for c in combo:
      product += tuplist[starting_element][tup_element + c]
      starting_element += 1
      tup_element += c
      print(product)
    print(combo, product)


if __name__ == '__main__':
  tup1 = (
      (1,),
      (2, 3),
      (3, 3, 1),
      (3, 1, 5, 4),
      (3, 1, 3, 1, 3),
      (2, 2, 2, 2, 2, 2),
      (5, 6, 4, 5, 6, 4, 3)
  )
  tup2 = (
      (1,),
      (2, 1),
      (1, 2, 1),
      (1, 2, 1, 1),
      (1, 2, 1, 1, 1),
      (1, 2, 1, 1, 1, 1),
      (1, 2, 1, 1, 1, 1, 9)
  )
  tup3 = (
      (9,),
      (2, 2),
      (3, 3, 3),
      (4, 4, 4, 4)
  )
  count_gold(tup2)
  count_gold(tup3)
