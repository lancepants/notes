#!/usr/bin/python3
'''
TODO:
- comment and make not so gross. Yecch
- final line doesn't pad remaining space with whitespace

Given a string of words and a length, L, format the text such 
that each line has exactly L characters and is fully (left 
and right) justified.

You should pack your words in a greedy approach; that is,
pack as many words as you can in each line. Pad extra spaces
with ' ' when necessary so that each line has exactly L chars

Extra spaces between words should be distributed as evenly as
possible. If the number of spaces on a line does not divide
evenly between the words, the empty slots on the left will be
assigned more spaces than the slots on the right.

For the last line of text, it should be left justified and no
extra space is inserted between the words.

For example:
    words = "This is an example of text justification."
    L = 16
returns as:
    [
      "This    is    an",
      "example  of text",
      "justification.  "
    ]

Each word is guaranteed not to exceed L in length.
'''
import math
def justify(text, width):
    ret = []
    wlist = text.split()
    # get number of required lines. Round up.
    numlines = math.ceil(len(text)/width)
    lines = {}
    for l in range(numlines):
        lines[l] = ""
        remain = width + 1
        for w in wlist[:]:
            if remain > len(w):
                lines[l] = lines[l] + w + " "
                remain -= len(w) + 1
                wlist.remove(w)
            else:
                break
    for line in lines.values():
        alphacount = 0
        wordcount = len(line.split())
        for c in line:
            if c.isalpha():
                alphacount += 1
        whitespacefill = width - alphacount
        if wordcount > 1:
            spaces = int(whitespacefill / (wordcount - 1))
        else:
            spaces = 0
        if spaces > 0:
            spacer = ' '*spaces
        else:
            spacer = ' '
        ret.append(spacer.join(line.split()))
    for line in ret:
        if len(line) < width:
            line = line.replace(' ', '  ', 1)
        print(line)


if __name__ == '__main__':
    justify("Here is some text to justify. I hope that this works.", 16)
    justify("The quick brown fox jumped over the lazy dog. It continued on into the chicken coop, where it slaughtered several baby chicks.", 25)
