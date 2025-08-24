# Given a string, return the number of alphabets (upper and lower case), integers, and special characters (@, #, etc.). Spaces do not count.

import string

def check_integer(str):
    if str.isdigit():
        return True
    else: 
        return False

def character_counter(str):
    alphabet = 0
    integers = 0
    special = 0

    for i in range(len(str)):
        if str[i] == ' ':
            continue
        elif str[i] in string.ascii_letters:
            alphabet += 1
        elif check_integer(str[i]) is True:
            integers += 1
        else:
            special += 1
    
    result = "Number of letters: {falpha}\nNumber of integers: {fintegers}\nNumber of special characters: {fspecial}".format(falpha = alphabet, fintegers = integers, fspecial = special)

    return result
        

print("First test:\n", character_counter("john"))
print("Second test:\n", character_counter("John 117"))
print("Third test:\n", character_counter("S-117"))