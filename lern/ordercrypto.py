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
  alphalist = list(alphabet)
  for ele in crypto:
    numchars = len(ele)
    lookahead = numchars-1
    if numchars <= 1:
      continue
    for i in range(numchars):
      while True:
        if ele[i] > ele[i+lookahead]:
          alphalist.remove(ele[i])
          alphalist.insert(alphalist.index(ele[i+lookahead]), ele[i])
        elif ele[i] < ele[i+lookahead]:
          alphalist.remove(ele[i+lookahead])
          alphalist.insert(alphalist.index(ele[i]), ele[i+lookahead])
        lookahead -= 1
        if lookahead < 1:
          break
  print(''.join(alphalist))


if __name__ == '__main__':
  checkio(["acb", "bd", "zwa"])
  #checkio(["klm", "kadl", "lsm"])
  #checkio(["a", "b", "c"])
  #checkio(["aazzss"])
  #checkio(["dfg", "frt", "tyg"])
