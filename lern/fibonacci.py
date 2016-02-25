#!/usr/bin/python3
'''
The fibonacci series is a series of numbers in which each number (Fibonacci
number) is the sum of the two preceding numbers. The simplest is the series 1,
1, 2, 3, 5, 8, 13, 21 etc.

It's a common example used when learning recursion. Its inefficiency also leads
to an alternate, iterative, "dynamic programming" memoization solution.
'''

# Using recursion
def fib(n):
  if n < 2:
    return 1
  return fib(n-1) + fib(n-2)

# Instead of recursion, iterate by populating a table using the previous two
# values in said table.
def fibdp(n):
  fibresult = {}
  # populate our first two values, aka "base cases"
  fibresult[0] = 1
  fibresult[1] = 1
  for i in range(2,n):
    fibresult[i] = fibresult[i-1] + fibresult[i-2]
  return fibresult.values()


# See which of these takes longer
for i in range(1,40):
  print(fib(i))

fibdp(40)
