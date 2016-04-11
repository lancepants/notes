#!/usr/bin/python3
'''
Suppose we could access yesterday's stock prices as a list, where:

- The indices are the time in minutes past trade opening time, which was 9:30am
  local time.
- The values are the price in dollars of Apple stock at that time.

So if the stock cost $500 at 10:30am, stock_prices_yesterday[60] = 500.

  stock_prices_yesterday = [10, 7, 5, 8, 11, 9]

  get_max_profit(stock_prices_yesterday)
  # returns 6 (buying for $5 and selling for $11)
'''


def get_max_profit(pricelist):
  '''
  First approach compares every value with every other value that follows it.
  Add each delta to a list and then return the max
  Complexity: O(n^2) , so not awesome
  '''
  deltas = []
  for m,p in enumerate(pricelist):
    maxdiff = -900
    for i in range(m+1,len(pricelist)):
      diff = pricelist[i] - pricelist[m]
      deltas.append(diff)
  print(deltas)
  print(max(deltas))


def take2(pricelist):
  '''
  Let's try to solve in O(n) time...
  '''
  lowestprice = pricelist[0]
  maxprofit = pricelist[1] - pricelist[0]
  for currentprice in pricelist[1:]:
    potentialprofit = currentprice - lowestprice
    maxprofit = max(maxprofit, potentialprofit)
    lowestprice = min(lowestprice, currentprice)
  print(maxprofit)

def icake_solution(stock_prices_yesterday):
    # make sure we have at least 2 prices
    if len(stock_prices_yesterday) < 2:
        raise IndexError('Getting a profit requires at least 2 prices')

    # we'll greedily update min_price and max_profit, so we initialize
    # them to the first price and the first possible profit
    min_price = stock_prices_yesterday[0]
    max_profit = stock_prices_yesterday[1] - stock_prices_yesterday[0]

    for index, current_price in enumerate(stock_prices_yesterday):
        # skip the first (0th) time
        # we can't sell at the first time, since we must buy first,
        # and we can't buy and sell at the same time!
        # if we took this out, we'd try to buy /and/ sell at time 0.
        # this would give a profit of 0, which is a problem if our
        # max_profit is supposed to be /negative/--we'd return 0!
        if index == 0:
            continue

        # see what our profit would be if we bought at the
        # min price and sold at the current price
        potential_profit = current_price - min_price
        # update max_profit if we can do better
        max_profit = max(max_profit, potential_profit)
        # update min_price so it's always
        # the lowest price we've seen so far
        min_price  = min(min_price, current_price)

    return max_profit


if __name__ == '__main__':
  get_max_profit([10,7,5,8,11,9])
  get_max_profit([10,20,5,8,11,9])
  get_max_profit([20,10,8,2])
  take2([10,7,5,8,11,9])
  take2([10,20,5,8,11,9])
  take2([20,10,8,2])
