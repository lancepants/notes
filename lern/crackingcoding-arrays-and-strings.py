#!/usr/bin/python3
'''
Some of the shorter tasks from cracking the coding interview.
'''

# Implement an algorithm to determine if a string has all unique characters. 
def allunique(stringy):
  if len(stringy) == len(set(stringy)):
    return True
  else:
    return False
# What if you cannot use additional data structures?
def uniqstr(stringy):
  for i,c in enumerate(stringy[:-1]):
    if c == stringy[i+1]:
      print("Match found. Not unique.")
      return False
  print("All unique chars")
  return True


# Given two strings, write a method to decide if one is a permutation of the
# other
import itertools
def permu(str1, str2):
  if sorted(str1) == sorted(str2):
    return True
  # Alternately, use itertools
  str1iters = list(itertools.permutations(str1))
  if str2 in str1iters:
    return True
  return False


# Write a method to replace all spaces in a string with '%20', and remove extra
# spaces from the end of the string.
def spacereplace(stringy):
  return stringy.rstrip().replace(' ', '%20')


# Implement a method to perform basic string compression using the counts of
# repeated characters. For example, aabcccccaaa should return a2b1c5a3. If your
# compressed string does not end up smaller than original str, return original
import re
from itertools import groupby
def compression(stringy):
  compressed = []
  # Can't use dicts to char count here, cause a character can appear twice
  #{c:stringy.count(c) for c in set(stringy)}
  # Can't use str.count('c') for same reason.

  # We can use regex, but it's weird, we have to use itertools as re.findall()
  # will only return the single-character group match rather than the whole
  # greedy match. You could do re.findall(r'(\w)(\1*)', stringy) to get a list
  # of tups where tup[0] is initial char, and tup[1] is the rest of the
  # repeated chars (if any). Alternately, use finditer
  matcher = re.compile(r'(\w)\1*')
  groups = [match.group() for match in matcher.finditer(stringy)]

  # Alternately, we can use groupby which makes tups where tup[0] is your "key"
  # char and tup[1] is a grouping of that char
  groups = [''.join(grouping) for c, grouping in groupby(stringy)]

  for g in groups:
    compressed.append('{}{}'.format(g[0],len(g)))
  ret = ''.join(compressed)

  if len(ret) < len(stringy):
    print(ret)
    return ret
  else:
    print(stringy)
    return stringy


'''
Write an algorithm such that if an alement in an MxN matrix is 0, its entire
row and column are set to 0

-gather all 0 coords
-do a set() against x and y coords
-change all coords in those columns/rows to 0
'''

'''
Assume you have a method isSubstring which checks if one word is a
substring of another. Given two strings, si and s2, write code to check if s2
is a rotation of si using only one call to isSubstring (e.g.,"waterbottle"is a
rota-tion of "erbottlewat")
'''

if __name__ == '__main__':
  compression('aaaabbc')
  compression('abc')
