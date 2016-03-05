#!/usr/bin/python3
'''
The Robots have found an encrypted message. We cannot decrypt it at the moment, but we can take the first steps towards doing so. You have a set of "words", all in lower case, and each word contains symbols in "alphabetical order". (it's not your typical alphabetical order, but a new and different order.) We need to determine the order of the symbols from each "word" and create a single "word" with all of these symbols, placing them in the new alphabetial order. In some cases, if we cannot determine the order for several symbols, you should use the traditional latin alphabetical order. For example: Given words "acb", "bd", "zwa". As we can see "z" and "w" must be before "a" and "d" after "b". So the result is "zwacbd".

Input: Words as a list of strings.

Output: The order as a string.

Example:

    checkio(["acb", "bd", "zwa"]) == "zwacbd"
    checkio(["klm", "kadl", "lsm"]) == "kadlsm"
    checkio(["a", "b", "c"]) == "abc"
    checkio(["aazzss"]) == "azs"
    checkio(["dfg", "frt", "tyg"]) == "dfrtyg"
'''

'''
for c in each ele see if c's position when compared to all characters in ahead
of it lines up with the normal alphabet. If not, move it in front of offending
character and move all other characters down (listy.insert(index, "blah")))
then iterate over new alphabet and print if char is in a joined + uniq'd input
string (eg: "acbbdzwa")
'''

def checkio(crypto):
  alphabet='abcdefghijklmnopqrstuvwxyz'
  alpharank = {}
  # generate an indexed ranking of letters. Spread has to be longer in length
  # than the longest input list element, ie 100 is good for 100 chars.
  hundreds = 100
  for index, char in enumerate(alphabet):
    alpharank[char] = (index+1) * hundreds

  for chars in crypto:
    remaining = len(chars)

    # Mark the first character as our "pivot" comparison. Always compare it
    # against the last character in the string, then recurse again with the
    # formerly last character removed.
    def recurse(rchars, rremaining):
      if alpharank[rchars[0]] > alpharank[rchars[-1]]:
        alpharank[rchars[0]] = alpharank[rchars[-1]] - rremaining
      rremaining -= 1
      if rremaining > 1:
        recurse(rchars[:-1], rremaining)

    # Pass the recursion function a slice from current iteration character
    # to end of the string.
    for i, c in enumerate(chars):
      recurse(chars[i:], len(chars[i:]))
    print(sorted(alpharank.items(), key=lambda x: x[1]))

  # TODO: concatenate input characters, uniq them, then print them in ranked
  # order as mapped in alpharank.



if __name__ == '__main__':
  checkio(["zwa"])

  #e 500
  #c 300
  #a 100
  ## subtract len(elem)
  #e 97
  #c 300
  #a 100
  ## compare 99 against 300
  #e 99
  #c 300
  #a 100
  ## on to our next char, subtract len(elem)-1
  #e 97
  #c 98
  #a 100
  checkio(["acb", "bd", "zwa"])
  #checkio(["klm", "kadl", "lsm"])
  #checkio(["a", "b", "c"])
  #checkio(["aazzss"])
  #checkio(["dfg", "frt", "tyg"])
