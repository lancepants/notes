#!/usr/bin/python3
'''
This script pulls words from a wordlist and sanitizes the list for
use with qutebrowser such that hints work properly. It does this by
removing hintlist elements that have a partial string match.

eg:
    hint1 = "zoo"
    hint2 = "zoom"

If these two hints show up on a page at the same time, you will
never be able to get to hint "zoom" as you have to type "zoo" first.
This doesn't work anyways, qutebrowser will crash.

TODO:
-list.remove("element") is expensive, each time it is called it goes
through the entire list. Look for ways to refactor this.
-make this thing support an arbitrary number of characters range
'''
smallwords = []
threes = []
fours = []
with open("/home/llaursen/filtered-wordlist","r") as f:
    for w in f:
        w = w.strip("\n")
        if len(w) == 3:
            threes.append(w)
        if len(w) == 4:
            fours.append(w)


for threec in threes:
    # Doing list[:] creates a NEW list object to iterate over. This lets
    # you use list.remove("something") within your for loop without
    # screwing up the index, since indexes are changing only on the
    # original object as you remove stuff.
    for fourc in fours[:]:
        if threec in fourc:
            print("FOUND " + threec + " IN " + fourc)
            fours.remove(fourc)

smallwords = sorted(threes+fours)

with open("/home/llaursen/smallwords-vifriendly.txt","w") as swfile:
    for sw in smallwords:
        swfile.write(sw+"\n")

