# ABANDONED DUE TO LACK OF OPTIMIZATION OF FUNCTIONS BETWEEN SCRIPTS

# script that creates a "random number" by generating 100 or so at the start of a game
# from tests, getting random numbers can take almost 0.1 second per random.randint
# however this takes about 20 seconds & doesn't correctly provide numbers, as python imports scripts weirdly

import random

pseudo_numbers = [0,1]
i = 0
pseudo_initiated = False

def init_pseudo_rand(_amount):
    global pseudo_initiated
    if not pseudo_initiated:
        pseudo_numbers = []
        for j in range(_amount):
            pseudo_numbers.append(random.getrandbits(4)) # generates a random 4-bit number (0-16)
        
        for n in pseudo_numbers:
            print(str(pseudo_numbers[n]))
        pseudo_initiated = True

def get_pseudo_rand():
    global pseudo_initiated
    global i
    
    if pseudo_initiated:
        i += 1
        
        if i >= len(pseudo_numbers):
            i = 0
        return pseudo_numbers[i]
    else:
        return 0