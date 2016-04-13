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

TODO:
- Currently O(n^2). This can very likely be done in less time...
- Avoid duplicate work by remembering already-calculated products
'''

import itertools
def count_gold(tuplist):
  # A tree's depth starts at 0
  depth = len(tuplist) - 1

  # maximum number of paths in this case happens to be 2^tree_depth
  maxpaths = 2**depth

  # itertools.product will return all possible combo's of  given elements,
  # within a length given (repeat). Using list comp to output lists instead
  # of tups from the iter object.
  combos = [list(c) for c in itertools.product([0, 1], repeat=depth)]

  # Initialize largest product we've seen so far
  max_so_far = tuplist[0][0]

  for combo in combos:
    # Set initial product to the item we will always be adding from
    product = tuplist[0][0]
    # Start at the second element in tuplist
    starting_element = 1
    # Start at index 0 for each combo
    tup_element = 0

    # Store the largest product seen so far

    for c in combo:
      product += tuplist[starting_element][tup_element + c]
      starting_element += 1
      tup_element += c

    #print(combo, product, max_so_far)

    if product > max_so_far:
      max_so_far = product

  print(max_so_far)



def checkio_top(pyramid):
  '''
  Approach
  --------
  
  This algorithm is a greedy approach to solving the problem.  
  Instead of working forward through the pyramid, we will work backwards.
  The idea is to start in the second to bottom row and select maxium of the
  the next two possible values from the current node and add that value to 
  the current node.
  
  After that we continue to roll up the rows and repeat the process for each
  node in that row.  When we reach the starting node we will have the sum
  of the maximum path.  
  
  *Note*: we are not finding the best path; we are only finding the maxium sum 
  from that path.  
  
  Code
  ----
  
  I want a mutable copy of the pyramid to work with.  
  Get the number of rows from the **len** function.  
  The last row is not in play to start hence **rows-1**
  Also we're working backwards so use the **reversed** function.
  Need to itertate over each item in the row. Note the plus 1, range(0) 
  returns an empty list.
  The possible nodes to examine are 1) the on directly below i+1,j
  and the one below and to the right i+1, j+1.  We use the **max** 
  function to select the largest one and then add it to the current
  node.  
  
  '''
  py = [list(i) for i in pyramid]
  for i in reversed(range(len(py)-1)):   
    for j in range(i+1):
      py[i][j] +=(max(py[i+1][j], py[i+1][j+1]))
  return py[0][0]




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
  count_gold(tup1)  # 23
  count_gold(tup2)  # 15
  count_gold(tup3)  # 18

