#!/usr/bin/python3
'''
Your company built an in-house calendar tool called HiCal.
You want to add a feature to see the times in a day when 
everyone is available.

To do this, you’ll need to know when any team is having a 
meeting. In HiCal, a meeting is stored as tuples of 
integers (start_time, end_time). These integers represent 
the number of 30-minute blocks past 9:00am.

For example:

  (2, 3) # meeting from 10:00 – 10:30 am
  (6, 9) # meeting from 12:00 – 1:30 pm

Write a function condense_meeting_times() that takes a list 
of meeting time ranges and returns a list of condensed 
ranges.

For example, given:

  [(0, 1), (3, 5), (4, 8), (10, 12), (9, 10)]

your function would return:

  [(0, 1), (3, 8), (9, 12)]

The second value is when it ends...that means from 8 to 9 
people are free.

Do not assume the meetings are in order. The meeting times 
are coming from multiple teams.

Write something that's efficient even when we can't put a 
nice upper bound on the numbers representing our time 
ranges.

- build a list of len(max(tuplist)), fill with range vals
- check if diff > 1 exists between elements
- 
'''

def condense_meeting_times(tuplist):
  # First build a list of busy times. Range naturally
  # does end_time - 1. If a time ends at 8, that means
  # that 7 through 7.99 is in busy_time.
  busy_times = []
  for tup in tuplist:
    start_time = tup[0]
    end_time = tup[1]
    for n in range(start_time, end_time):
      busy_times.append(n)
  busy_times = list(set(busy_times))

  # Now go through list of busy times. If there is a
  # difference greater than 1, save our original
  # start_time, and the end_time plus 1 to a tuple
  # stored in ret.
  ret = []
  start_time = busy_times[0]
  for i,n in enumerate(busy_times):
    # We need to know when we are at the end in order
    # to generate the last tuple. Can't 
    # just enumerate(busy_times[:-1])
    if i == len(busy_times)-1:
      ret.append((start_time, busy_times[i]+1))
      break
    diff = busy_times[i+1] - n
    if diff > 1:
      ret.append((start_time, busy_times[i]+1))
      start_time = busy_times[i+1]
      continue

  print(ret)

if __name__ == '__main__':
  condense_meeting_times([(0, 1), (3, 5), (4, 8), (10, 12), (9, 10)])  # [(0, 1), (3, 8), (9, 12)]
