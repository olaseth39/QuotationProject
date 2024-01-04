// Define an object that maps numbers to their word form
const numbersToWords = { 0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",8: "eight",
                        9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
                        16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty", 30: "thirty",
                        40: "forty", 50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety",
                        };

# for values < 10
ONES_ = {0:"", 1:"One", 2:"Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six",7: "Seven",8: "Eight", 9: "Nine"}

# for values < 20
TEENS_ = {0:"Ten", 1:"Eleven", 2:"Twelve", 3:"Thirteen", 4:"Fourteen", 5:"Fifteen", 6:"Sixteen",
            7:"Seventeen", 8:"Eighteen", 9:"Nineteen"}

# for values >20 but < 100
TENS_ = {0:"", 1:"", 2:"Twenty", 3:"Thirty", 4:"Forty", 5:"Fifty", 6:"Sixty", 7:"Seventy", 8:"Eighty", 9:"Ninety"}

// Define the convertNumberToWords function
function convertNumberToWords(number) {
  // if number present in object no need to go further
  if (number in numbersToWords){
        return numbersToWords[number]
  }
  else if (number === 0){
        return 0;
  } else if (number < 0){
        return "minus" + convertNumberToWords(math.abs(number))
  }else if (number < 10){
        return ONES_[number]
  }else if (number < 20){
        return TEENS_[number - 10]
  }else if (number < 100){
        return TENS_[math.floor(number / 10)] + " " + convertNumberToWords(number % 10)

  }else if (number < 1000){
        return ONES_[math.floor(number / 100)] + " Hundred " + " and " + convertNumberToWords(number % 100)
  }else if (number < 1000000){
        return ONES_[math.floor(number / 1000)] + " Thousand " + " and " + convertNumberToWords(number % 1000)
  }else if (number < 1000000000){
        return ONES_[math.floor(number / 1000000)] + " Million " + " and " + convertNumberToWords(number % 100)
  }else if (number < 1000000000000){
        return ONES_[math.floor(number / 1000000000)] + " Billion " + " and " + convertNumberToWords(number % 100)
  }else {
        return "Figure very Large"
        }
}

console.log(convertNumberToWords(123));