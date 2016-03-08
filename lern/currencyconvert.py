#!/usr/bin/python3
'''
Many countries use different conventions for the thousands separator and decimal mark. For example in the Netherlands one million one thousand two hundred and eighty one-hundredths is written as 1.001.200,80, but in the US this is written as 1,001,200.80. Use your coding skills to convert dollars in the first style (Netherlands, Germany, Russia, Turkey, Brazil, and others) to the second style (US, UK, Canada, China, Japan, Mexico, and others).

Only currency amounts in dollars should be converted: $1.234,50 to $1,234.50, $1.000 to $1,000, and $4,57 to $4.57. But don't convert your router's IP address 192.168.1.1. Also leave currency in the US style unchanged.

Input: A string containing dollar amounts to be converted.
Output: A string with converted currencies.

Example:
    checkio("Lot 192.001 costs $1.000,94.") == "Lot 192.001 costs $1,000.94."
    checkio("$1,23 + $2,34 = $3,57.") == "$1.23 + $2.34 = $3.57."
'''
import re
def checkio(stringy):
    newlinesanitized = stringy.replace('\n', 'NEWLINE')
    # Be explicit with split. Give it (' ') rather than just () or it won't split
    # on multiple spaces between words.
    words = newlinesanitized.split(' ')
    res = []
    for w in words:
        if "$" in w:
            if w[-1].isdigit():
                appendgrammar = ""
            else:
                appendgrammar = w[-1]
                w = w[:-1]
            w = w.replace(',', '.')
            dotcount = w.count('.')
            if dotcount > 1:
                w = w.replace('.', ',', dotcount-1)
            w = re.sub(r'\.(\d\d\d)', r',\1', w)
            if appendgrammar:
                res.append(w + appendgrammar)
            else:
                res.append(w)
        else:
            res.append(w)
    ret = ' '.join(res).replace('NEWLINE', '\n')
    return ret

'''
Top "clear" answer 
'''
def checkioTopClear(text):
        reform = lambda match: match.group(0).translate(str.maketrans(',.', '.,'))
        return re.sub('\$\d{1,3}(\.\d{3})*(,\d{2}){,1}(?!\d)', reform, text)

        # \$            letter '$'
        # \d{1,3}       [0-9] of length {1, 3}
        # (\.\d{3})*    repetation of \.[0-9]{3}, *if exists
        # (,\d{2}){,1}  ,[0-9]{2}, if exists ({,1} instead of *, though we could have used *, it's more correct for no or only one occurrence of ,\d\d here)
        # (?!\d)        no [0-9] after pattern, if something after pattern exists

# Once a match is found, it's passed to that lambda function which uses maketrans to swap , where it sees . and . where it sees ,.
#  This is ok because we never match more than the first part of US-based currency numbers (eg: $200,284.23 only has $200 matched, and $3.68 only has $3 matched, so maketrans does nothing as there are no , or .)

# Here's a less busy version:
def checkioSecondClear(text):
        EU2US = lambda match: match.group().translate({44: 46, 46: 44})
        return re.sub('\$\d{,3}(\.\d{3})*(,\d{2})?(?!\d)', EU2US, text)

if __name__ == '__main__':
    checkio("Lot 192.001 costs $1.000,94 and 2918.028 costs $5.028.281.247,36")
    checkio("$1,23 + $2,34 = $3,57.")
    checkio("$1.234, $5.678 and $9")  # "$1,234, $5,678 and $9"
    checkio("$222,100,455 and $827.123.737.124")
    checkio("Clayton Kershaw $31.000.000\nZack Greinke   $27.000.000\nAdrian Gonzalez $21.857.143\n") # notice the extra spaces after Greinke...
