#!/usr/bin/python3
'''
The alphabet contains both vowel and consonant letters (yes, we divide the
letters).
Vowels -- A E I O U Y
Consonants -- B C D F G H J K L M N P Q R S T V W X Z

You are given a block of stringy with different words. These words are separated
by white-spaces and punctuation marks. Numbers are not considered words in this
mission (a mix of letters and digits is not a word either). You should count
the number of words (striped words) where the vowels with consonants are
alternating, that is; words that you count cannot have two consecutive vowels
or consonants. The words consisting of a single letter are not striped -- do
not count those. Casing is not significant for this mission.

Input: A stringy as a string (unicode)

Output: A quantity of striped words as an integer.

Example:

  checkio("My name is ...") == 3
  checkio("Hello world") == 0
  checkio("A quantity of striped words.") == 1, "Only of"
  checkio("Dog,cat,mouse,bird.Human.") == 3
'''
import re
def checkio(stringy):
  vowels='aeiouy'
  consonants='bcdfghjklmnpqrstvwxz'
  numbers='0123456789'
  words = re.sub('[^A-Za-z0-9]+',' ', str.lower(stringy)).split()
  falsewords = []
  for word in words:
    if len(word) == 1:
      falsewords.append(word)
      continue
    for i in range(len(word)-1):
      if word[i] in numbers:
        falsewords.append(word)
        break
      if word[i] in consonants:
        if word[i+1] not in vowels:
          falsewords.append(word)
          break
      if word[i] in vowels:
        if word[i+1] not in consonants:
          falsewords.append(word)
          break
  print(len(words) - len(falsewords))
  return len(words) - len(falsewords)

'''
Here's a better solution!
'''
def checkiobetter(stringy):
    VOWELS = "AEIOUY"
    CONSONANTS = "BCDFGHJKLMNPQRSTVWXZ"
    PUNCTUATION = ",.!?"
    stringy = stringy.upper()
    for c in PUNCTUATION:
        stringy = stringy.replace(c, " ")
    for c in VOWELS:
        stringy = stringy.replace(c, "v")
    for c in CONSONANTS:
        stringy = stringy.replace(c, "c")
    words = stringy.split()
    count = 0
    for word in words:
        if len(word) > 1 and word.isalpha():
            if 'cc' not in word and 'vv' not in word:
                count += 1
    print(count)
    return count

if __name__ == '__main__':
  #checkio("My name is ...")
  #checkio("Hello world")
  #checkio("A quantity of striped words.")
  #checkio("Dog,cat,mouse,bird.Human ghost pepper derp. Lala")
  #checkio("A quantity of striped words.")  #1
  #checkio("1st 2a ab3er root rate")  #1
  checkiobetter("My name is ...")
  checkiobetter("Hello world")
  checkiobetter("A quantity of striped words.")
  checkiobetter("Dog,cat,mouse,bird.Human ghost pepper derp. Lala")
  checkiobetter("A quantity of striped words.")  #1
  checkiobetter("1st 2a ab3er root rate")  #1
