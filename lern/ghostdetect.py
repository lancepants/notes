#!/usr/bin/python3
'''
In the northern waters, sailors say they’ve seen Ghost Ship patrolling the waters. Nobody can see the other ships after they witness the Ghost Ship. This causes a problem: how do they distinguish a normal ship from the ghost ship in such dense fog? We can use a locator program for this.

For a normal ship, reflected signals have the same duration. So you wait for three signals and if they have the same durations, then we are safe because the ship is normal. If you see any difference - we’d better to run away, because that’s the Ghost Ship.

We have the old discrete locator, so test results look like a sequence of 1’s and 0’s, where each symbol is a value in seconds. 1 is a signal, 0 is pause. So “N” consecutive 1’s is a “N” seconds long signal. Pauses can be various lengths as well. The old locator shows test results as a number in decimal form, so you will need to convert it to binary form before analysis can begin. The binary form of our tests have the pattern r"1+0+1+0+1+" (regexp).

Let's look at some examples:
- The number on the locator is 21. It's "10101" in binary form and we see 3 signals with 1 second duration each. This is a normal ship.
- The number is 1587. The binary form is "11000110011” and we see 3 signals with 2 seconds duration but with various pauses. It's ok.
- The number is 3687. The binary form - "111001100111” and we see 3 signals. Two signals with 3 seconds duration and one with 2 seconds. It's a good idea to run away.

You are given a number and your mission is recognize if this number reveals a normal ship (True) or not (False).

We have one more rule for this challenge. This is a code golf mission and your main goal is to make your code as short as possible. The shorter your code, the more points you earn. Your score for this mission is dynamic and directly related to the length of your code. For reference, scoring is based on the number of characters used. 200 characters is the maximum allowable and it will earn you zero points. For each character less than 200, you earn 1 point. For example for 150 character long code earns you 50 points. In this mission we count whitespaces, but don't count indents.

Input: A number as an integer.
Output: Is it a normal ship or not as a boolean.
Example:

  recognize(21) == True
  recognize(1587) == True
  recognize(3687) == False
'''
# split on 0 of arbitrary length. if len of each group of 1's is the same, then it's a normal ship. Else, ghost
# 100 chars!
import re
def recognize(d):
  b=re.split('0+',bin(d)[2:])
  print(all(len(s)==len(b[0]) for s in b))


# this one is neat too. Notice the initial match (1+) and then 
# the following (\1)'s to match the same sequence of 1's.
import re
def recognize(number):
      return re.compile(r'(1+)0+(\1)0+(\1)$').match(bin(number), 2) != None

if __name__ == '__main__':
  recognize(21)
  recognize(1587)
  recognize(3687)
