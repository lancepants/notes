#!/usr/bin/env python
'''
The general quicksort steps are:
1) Pick an element, called a *pivot*, from the array

2) Partitioning: reorder the array so that all elements with
values less than the pivot point come before the pivot, while all
elements with values grater than the pivot come after it (equal values
go either way). After this partitioning, the pivot is in its final
position. This is called the **partition** operation

3) Recursively apply the above steps to the sub-array of elements
with smaller values, and separately do the same to the sub-array
with the higher values
'''

def quicksort(listy, lowi, highi):
  pivot = highi
  if lowi < highi:
    p = partition(listy, lowi, highi)
    quicksort(listy, lowi, p - 1)
    quicksort(listy, p + 1, highi)
  print listy

def partition(listy, lowi, highi):
  '''
  This def does the position swapping among items in the list
  and then returns a new pivot index (??)
  '''
  # Set the pivot to the final value in the list
  # we will compare this index's value to the other
  # values in the partition
  pivot = listy[highi]
  # Set working index to the first index in the partition
  # this is what we will increment as we move up the
  # list and compare values
  i = lowi
  # Go through all elements in the partition, minus the
  # very last item which is the pivot
  for ele in range(lowi, highi):
    # If the value at the index we are processing is less than
    # or equal to the pivot value
    if listy[ele] <= pivot:
      swapsaver = listy[ele]
      listy[ele] = listy[i]
      listy[i] = swapsaver
      i += 1
    # not sure why to swap here?
    finalswapsaver = listy[i]
    listy[i] = listy[highi]
    listy[highi] = finalswapsaver
    return i

if __name__ == '__main__':
  f = [2,5,2,1,9,8,8,2,6]
  res = quicksort(f, 0, len(f))
