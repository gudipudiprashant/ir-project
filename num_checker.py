# Num checker


def is_number(num_string):
  try:
    int(num_string)
    return True
  except ValueError:
    return False


units = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
  ]

tens = [ "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

scales = ["hundred", "thousand", "million", "lakh", ]
nums = set(units+tens+scales)
