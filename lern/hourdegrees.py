#!/usr/bin/python3
'''
Analog clocks display time with an analog clock face, which consists of a round dial with the numbers 1 through 12, the hours in the day, around the outside. The hours are indicated with an hour hand, which makes two revolutions in a day, while the minutes are indicated by a minute hand, which makes one revolution per hour. In this mission we will use a clock without second hand. The hour hand moves smoothly and the minute hand moves step by step.

You are given a time in 24-hour format and you should calculate a lesser angle between the hour and minute hands in degrees. Don't forget that clock has numbers from 1 to 12, so 23 == 11. The time is given as a string with the follow format "HH:MM", where HH is hours and MM is minutes. Hours and minutes are given in two digits format, so "1" will be writen as "01". The result should be given in degrees with precision ±0.1.

clocks

For example, on the given image we see "02:30" or "14:30" at the left part and "01:42" or "13:42" at the right part. We need to find the lesser angle.

Input: A time as a string.

Output: The lesser angle as an integer or a float.

Example:

  clock_angle("02:30") == 105
  clock_angle("13:42") == 159
  clock_angle("01:43") == 153.5
'''

def clock_angle(time):
  # each minute is 6 degrees
  # each hour (00am-11:59am) * 30 = degrees
  # minute/60 = hourpoint  ;  hour.hourpoint * 30 = degrees
  # subtract 12 from each hour 12 or over?

  splittime = time.split(':')
  hourpoint = int(splittime[1])/60.0
  hour = int(splittime[0]) + hourpoint
  hourdegrees = hour*30
  minutedegrees = int(splittime[1])*6

  # abs() will convert a negative to a positive, and
  # keep a positive a positive.
  diff = abs(hourdegrees - minutedegrees)

  # This also takes care of 24hr times...
  if diff > 180:
    ret = abs(360 - diff)
  else:
    ret = diff

  print(ret)


if __name__ == '__main__':
  clock_angle("02:30")
  clock_angle("13:42")
  clock_angle("01:43")
  clock_angle("15:50")
  clock_angle("12:00")
  clock_angle("02:30") # 105, "02:30"
  clock_angle("13:42") # 159, "13:42"
  clock_angle("01:42") # 159, "01:42"
  clock_angle("01:43") # 153.5, "01:43"
  clock_angle("00:00") # 0, "Zero"
  clock_angle("12:01") # 5.5, "Little later"
  clock_angle("18:00") # 180, "Opposite"
