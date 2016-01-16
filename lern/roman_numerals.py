#!/usr/bin/python3
'''
Convert a given number into its roman numeral.

The first ten roman numerals are:
I, II, III, IV, V, VI, VII, VIII, IX, and X

The remaining symbols are:
I 1 (unus)
V 5 (quinque)
X 10 (decem)
L 50 (quinquaginta)
C 100 (centum)
D 500 (quingenti)
M 1000 (mille)

Symbols are placed from left to right in order of value, starting with
the largest. However, in a few specific cases, to avoid four characters
being repeated in succession (such as IIII or XXXX), subtractive
notation is often used as follows:

  I placed before V or X indicates one less, so four is IV (one less
    than five) and nine is IX (one less than ten)
  X placed before L or C indicates ten less, so forty is XL (ten less
    than fifty) and ninety is XC (ten less than a hundred)
  C placed before D or M indicates a hundred less, so four hundred is
    CD (a hundred less than five hundred) and nine hundred is CM (a
    hundred less than a thousand)

Oddballs:
IV  4
IX  9
XL  40
XC  90
CD  400
CM  900

Our given number will be an integer ranging from 1 to 3999:
0 < number < 4000
'''

def checkio(num):
    result = ''
    symbols = {1000:"M",500:"D",100:"C",50:"L",10:"X",5:"V",1:"I"}
    oddballs = [("DCCCC","CM"),("CCCC","CD"),("LXXXX","XC"),("XXXX","XL"),("VIIII","IX"),("IIII","IV")]
    # Convert number to base roman numerals
    for key in sorted(symbols.keys(), reverse=True):
        while num >= key:
            result += symbols[key]
            num -= key
    # Some Roman's didn't like printing four characters in a row (eg: XXXX = 40), so
    # extra rules were made. Match and replace these oddball 4's and 9's from largest to smallest.
    for oddball, abbrev in oddballs:
        if oddball in result:
            result = result.replace(oddball, abbrev)
    print(result)
    return result


if __name__ == '__main__':
    checkio(4)
    checkio(9)
    checkio(40)
    checkio(90)
    checkio(400)
    checkio(900)
    print("")
    checkio(473)
    checkio(4)
    checkio(6)
    checkio(76)
    checkio(13)
    checkio(44)
    checkio(3999)

'''
checkio(473) == 'CDLXXIII'
checkio(6) == 'VI'
checkio(76) == 'LXXVI'
checkio(13) == 'XIII'
checkio(44) == 'XLIV'
checkio(3999) == 'MMMCMXCIX'
'''

# I could have just done this!
elements = { 1000 : 'M', 900 : 'CM', 500 : 'D', 400 : 'CD',
             100 : 'C', 90 : 'XC', 50 : 'L', 40: 'XL',
             10 : 'X', 9 : 'IX', 5 : 'V', 4: 'IV', 1 : 'I' }
def checkio(data):
    roman = ''
    for n in sorted(elements.keys(), reverse=True):
        while data >= n:
            roman += elements[n]
            data -= n
    return roman

