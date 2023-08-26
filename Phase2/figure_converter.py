

# we want to convert the value of our total price in words

# for values < 10
ONES_ = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]

# for values < 20
TEENS_ = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]

# for values >20 but < 100
TENS_ = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def convert_to_words(num):
    if int(num) == 0:
        return "zero"
    elif int(num) < 0:
        return "minus " + convert_to_words(abs(num))
    elif int(num) < 10:
        return ONES_[num]
    elif int(num) < 20:
        return TEENS_[num - 10]
    elif int(num) < 100:
        return TENS_[num // 10] + (" " + convert_to_words(num % 10) if num % 10 != 0 else "")
    elif int(num) < 1000:
        return ONES_[num // 100] + " Hundred" + (" and " + convert_to_words(num % 100) if num % 100 != 0 else "")
    elif int(num) < 1000000:
        return convert_to_words(num // 1000) + " Thousand" + \
               ("  " + convert_to_words(num % 1000) if num % 1000 != 0 else "")
    elif int(num) < 1000000000:
        return convert_to_words(num // 1000000) + " Million" + \
               ("  " + convert_to_words(num % 1000000) if num % 1000000 != 0 else "")
    elif int(num) < 1000000000000:
        return convert_to_words(num // 1000000000) + " Billion " + \
               (" " + convert_to_words(num % 1000000000) if num % 1000000000 != 0 else "")
    else:
        return "Figure very large"

