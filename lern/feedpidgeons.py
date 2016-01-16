#!/usr/bin/python3
'''
!!!UPDATE ME. ANSWER IS ON CHECKIO. THIS ONE HAS BUGS!!!

I start to feed one of the pigeons. A minute later two more fly by and a minute
after that another 3. Then 4, and so on (Ex: 1+2+3+4+...). One portion of food
lasts a pigeon for a minute, but in case there's not enough food for all the
birds, the pigeons who arrived first ate first. Pigeons are hungry animals and
eat without knowing when to stop. If I have N portions of bird feed, how many
pigeons will be fed with at least one portion of wheat?

Eg: five portions of wheat. checkio(5) == 3
    1st minute, N=4, one bird
    2nd minute, N=1, three birds (one on its second filling)
    3rd minute, N=0, six birds, no more food

Over this process, only 3 birds have eaten. The original bird has eaten 3 times,
and two birds from the second minute have eaten once. The rest have not.
'''
def checkio(n):
    portionsremaining = n
    birdcount = 0
    minute = 0
    while portionsremaining > 0:
        minute += 1
        prevbcount = birdcount
        birdcount += minute + birdcount
        if birdcount <= portionsremaining:
            portionsremaining -= birdcount
        else:
            birdsfed = prevbcount + portionsremaining
            print(birdsfed)
            return birdsfed

        # 1 bird fed, 4 portions remaining
        # 3 birds fed, 1 portion remaining
        # 3 birds fed, 0 portions remaining


if __name__ == '__main__':
    checkio(1) # 1 pidgeon fed
    checkio(2) # 1 pidgeon fed
    checkio(5) # 3 pidgeon fed
    checkio(10) # 6 pidgeon fed
    checkio(20)
    checkio(40)
