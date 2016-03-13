#!/usr/bin/python3
'''
http://www.checkio.org/mission/mono-captcha/

Your program should read the number shown in an image encoded as a binary matrix. Each digit can contain a wrong pixel, but no more than one for each digit. The space between digits is equal to one pixel (just think about "1" which is narrower than other letters, but has a width of 3 pixels).


Input: An image as a list of lists with 1 or 0.
Output: The number as an integer.
Example:

checkio([[0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0],
         [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
         [0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
         [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
         [0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0]]) == 394
checkio([[0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0],
         [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
         [0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
         [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0],
         [0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0]]) == 394
    
How it is used: This task will show you how optical character recognition works and will familiarize you with low-resolution fonts requiring noise-immunity. This can be useful for the systems that required the reliability.

Precondition: matrix_rows == 5
5 ≤ matrix_columns < 30
∀ x ∈ matrix : x == 0 or x == 1
digit_width == 3
Each digit contains no more than one wrong pixel.
digits_space == 1
'''
# generate a flat list of numbers 0 through 9, where width=3+1space
# take len() of input list and divide by 4 to see how many digits there are
# read first 4 eles of each input list, flatten into single list, compare against 0-9,
# read next 4 eles (if avail), etc. One error ok, more not. Go to next, or return nothing

def checkio(matrix):
  ret = ''
  # Numbers 0 through 9, flattened, with a spacer
  lnums = [
    [0,1,1,0,0,1,0,1,0,1,0,1,0,1,0,1,0,0,1,1],
    [0,0,1,0,0,1,1,0,0,0,1,0,0,0,1,0,0,0,1,0],
    [0,1,1,1,0,0,0,1,0,0,1,1,0,1,0,0,0,1,1,1],
    [0,1,1,1,0,0,0,1,0,0,1,0,0,0,0,1,0,1,1,1],
    [0,1,0,1,0,1,0,1,0,1,1,1,0,0,0,1,0,0,0,1],
    [0,1,1,1,0,1,0,0,0,1,1,0,0,0,0,1,0,1,1,0],
    [0,0,1,1,0,1,0,0,0,1,1,1,0,1,0,1,0,0,1,1],
    [0,1,1,1,0,0,0,1,0,0,1,0,0,1,0,0,0,1,0,0],
    [0,1,1,1,0,1,0,1,0,1,1,1,0,1,0,1,0,1,1,1],
    [0,0,1,1,0,1,0,1,0,1,1,1,0,0,0,1,0,1,1,0]
  ]
  
  # How many digits we need to process
  numdigits = int(len(matrix[0])/4)
  
  # Flatten our input digits to one list each. Place in a dict.
  slicey = 0
  # Initialize dict with keys, empty list. Avoid KeyErrors later.
  dicky = {key: [] for key in range(numdigits)}
  for d in range(numdigits):
    for m in matrix:
      dicky[d] = dicky[d] + m[slicey:slicey+4]
    slicey += 4

  # Compare flattened input digits with numbers 0-9
  for k,v in dicky.items():
    # If perfect match (no noise)
    if v in lnums:
      # Add the index number of lnums to our return. This
      # corresponds with the number we are matching.
      ret += str(lnums.index(v))
      continue
    # Compare each digit against each digit of each number 0-9
    # if more than on error, move on to the next comparison
    for index, n in enumerate(lnums):
      errors = 0
      for i, d in enumerate(n):
        if d != v[i]:
          errors += 1
      if errors <= 1:
        # Add the index number of lnums to our return. This
        # corresponds with the number we are matching.
        ret += str(index)
      else:
        continue

  #return int(ret)
  print(int(ret))


'''
Top clear checkio
Not exactly time efficient, but clear
'''
FONT = ("-XX---X--XXX-XXX-X-X-XXX--XX-XXX-XXX--XX",
        "-X-X-XX----X---X-X-X-X---X-----X-X-X-X-X",
        "-X-X--X---XX--X--XXX-XX--XXX--X--XXX-XXX",
        "-X-X--X--X-----X---X---X-X-X-X---X-X---X",
        "--XX--X--XXX-XXX---X-XX---XX-X---XXX-XX-")
def checkioTopClear(image):
    digits = len(image[0]) // 4
    result = 0
    for d in range(digits):
        for v in range(10):
            if sum(image[j][4*d+i] != (FONT[j][4*v+i] == 'X')
                    for j in range(5) for i in range(1, 4)) <= 1:
                result = result * 10 + v
    return result


if __name__ == '__main__':
  checkio([[0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0],
           [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
           [0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
           [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
           [0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0]]) == 394
  checkio([[0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0],
           [0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
           [0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
           [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0],
           [0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0]]) == 394
