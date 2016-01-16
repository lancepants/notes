'''
Create a function that determines the winner of an X's and O's game.
For example, taking this as input:
[
"X.O",
"XX.",
"XOO"]
Should return the winner "X". If there is no winner, return "D"
'''
# Brute force method
def checkio(listy):
  #r0
  if listy[0][0] == listy[0][1] and listy[0][0] == listy[0][2] and listy[0][0] != ".":
      return listy[0][0]
  #r1
  if listy[1][0] == listy[1][1] and listy[1][0] == listy[1][2] and listy[1][0] != ".":
      return listy[1][0]
  #r2
  if listy[2][0] == listy[2][1] and listy[2][0] == listy[2][2] and listy[2][0] != ".":
      return listy[2][0]
  #c0
  if listy[0][0] == listy[1][0] and listy[0][0] == listy[2][0] and listy[0][0] != ".":
      return listy[0][0]
  #c1
  if listy[0][1] == listy[1][1] and listy[0][1] == listy[2][1] and listy[0][1] != ".":
      return listy[0][1]
  #c2
  if listy[0][2] == listy[1][2] and listy[0][2] == listy[2][2] and listy[0][2] != ".":
      return listy[0][2]
  #bs
  if listy[0][0] == listy[1][1] and listy[0][0] == listy[2][2] and listy[0][0] != ".":
      return listy[0][0]
  #fs
  if listy[0][2] == listy[1][1] and listy[0][2] == listy[2][0] and listy[0][2] != ".":
      return listy[0][2]
  #draw
  return "D"


# This result uses a grid of winning possibilities
def checkio(game_result):
    g = game_result
    # Define win conditions
    wins = [
            ((0,0),(1,0),(2,0)),
            ((0,1),(1,1),(2,1)),
            ((0,2),(1,2),(2,2)),
            ((0,0),(0,1),(0,2)),
            ((1,0),(1,1),(1,2)),
            ((2,0),(2,1),(2,2)),
            ((0,0),(1,1),(2,2)),
            ((0,2),(1,1),(2,0))
            ]
    # Loop through the players
    for l in ['X','O']:
        # Check each set of winning coordinates
        for win in wins:
            # Sum the number of characters in those coordinates
            # which match the player's letter
            s = sum([1 for cond in win if g[cond[0]][cond[1]]==l])
            # If all coordinates in a win condition match, the sum will
            # be three, return this letter and break
            if s == 3: return l
    # If both players and all win conditions are checked
    # without a winner, the game was a draw
    return 'D'


# This one is really cool. Make a list of possible rows, cols, and diags
# and then string match for XXX, OOO, else D
def checkio(result):
    rows = result
    cols = map(''.join, zip(*rows))
    diags = map(''.join, zip(*[(r[i], r[2 - i]) for i, r in enumerate(rows)]))
    lines = rows + list(cols) + list(diags)
    return 'X' if ('XXX' in lines) else 'O' if ('OOO' in lines) else 'D'
# In python3 map returns an iterator, which is why this solution is doing list(mapobj)
# Could repro this solution with something less complex.

# X
checkio([
    "X.O",
    "XX.",
    "XOO"])
# O
checkio([
    "OO.",
    "XOX",
    "XOX"])
# D
checkio([
    "OOX",
    "XXO",
    "OXX"])
# X
checkio([
    "...",
    "XXX",
    "OO."])
