'''
Stephen's speech module is broken. This module is responsible for his number pronunciation. He has to click to input all of the numerical digits in a figure, so when there are big numbers it can take him a long time. Help the robot to speak properly and increase his number processing speed by writing a new speech module for him. All the words in the string must be separated by exactly one space character. Be careful with spaces -- it's hard to see if you place two spaces instead one.

Input: A number as an integer.
Output: The string representation of the number as a string.

Precondition: 0 < number < 1000
'''
def checkio(intnum):
    num = str(intnum)
    lows={"0":'',"1":'one',"2":'two',"3":'three',"4":'four',"5":'five',"6":'six',"7":'seven',"8":'eight',"9":'nine'}
    oddballs={"10":'ten',"11":'eleven',"12":'twelve',"13":'thirteen',"14":'fourteen',"15":'fifteen',"16":'sixteen',"17":'seventeen',"18":'eighteen',"19":'nineteen',"20":'twenty',"30":'thirty',"40":'forty',"50":'fifty',"60":'sixty',"70":'seventy',"80":'eighty',"90":'ninety'}
    tys={"0":'',"2":'twenty',"3":'thirty',"4":'forty',"5":'fifty',"6":'sixty',"7":'seventy',"8":'eighty',"9":'ninety'}
    result = []
    final = ""
    if len(num) == 4:
        return "one thousand"
    if len(num) == 3:
        result.append(lows[num[0]] + " hundred")
        try:
            result.append(oddballs[num[1:]])
        except KeyError:
            result.append(tys[num[1]])
            result.append(lows[num[2]])
    if len(num) == 2:
        try:
            result.append(oddballs[num])
        except KeyError:
            result.append(tys[num[0]])
            result.append(lows[num[1]])
    if len(num) == 1:
        if num == "0":
            return "zero"
        else:
            return lows[num]
    print(' '.join(x for x in result if x != ''))
    #return ' '.join(x for x in result if x != '')

if __name__ == '__main__':
    checkio(312)
    checkio(1)
    checkio(0)
    checkio(11)
    checkio(100)
    checkio(88)
    checkio(230)
    checkio(10)

# Here's the #1 on checkio at the moment
def checkio(i):
    if i < 20:
        result = 'zero,one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,thirteen,fourteen,fifteen,sixteen,seventeen,eighteen,nineteen'.split(',')[i]
    elif i < 100:
        result = ',,twenty,thirty,forty,fifty,sixty,seventy,eighty,ninety'.split(',')[i//10]
        if i % 10:
            result += ' ' + checkio(i % 10)
    elif i < 1000:
        result = checkio(i // 100) + ' hundred'
        if i % 100:
            result += ' ' + checkio(i % 100)
    return result

# # four
# checkio(4)
# # one hundred forty three
# checkio(143)
# # twelve
# checkio(12)
# # one hundred one
# checkio(101)
# # two hundred twelve
# checkio(212)
# # forty
# checkio(40)

