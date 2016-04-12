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

def count_gold(tuplist):
  depth = len(tuplist) - 1
  maxpaths = 2**depth
  steps = {}


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
  for tuppy in tup1, tup2, tup3:
    count_gold(tuppy)
