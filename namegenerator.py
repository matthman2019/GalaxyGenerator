# maybe use this if this program doesn't work: https://github.com/Rickmsd/namemaker

from random import randint
import random
import tkinter as tk


vowels = ["a", "e", "i", "o", "u", "y"]
# dipthongs can be any combination of vowels
consonants = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "z"]

def weighted_randint(*args:tuple[int, float]) -> int:
    # check that the probabilities given equal 1
    probabilitySum = 0.0
    for possibilityTuple in args:
        probabilitySum += possibilityTuple[1]
    if abs(1 - probabilitySum) > 0.001:
        raise Warning("The sum of probabilities does not equal 1!")
    
    # the way this works is: we add the possibility[1] (the probability) to possibilitySum every iteration of the loop.
    # if randomNumber is less than possiblitySum, we return possibility[0].
    # otherwise, we keep going with the loop.
    possibilitySum = 0
    randomNumber = random.random()

    for possibility in args:
        possibilitySum += possibility[1]
        if randomNumber < possibilitySum:
            return possibility[0]
        else:
            continue

def chance_boolean(probabilityTrue:float=0.5) -> bool:
    if random.random() < probabilityTrue:
        return True
    else:
        return False

def random_from_list(givenList:list|tuple) -> any:
    return givenList[randint(0, len(givenList)-1)]


# this was used to test weighted_randint
'''
import matplotlib.pyplot as plt
occurances = [0, 0, 0, 0]
while True: 
    for i in range(2000):
        occurances[weighted_randint((0, 0.1), (1, 0.1), (2, 0.1), (3, 0.7))] += 1

    plt.bar([0, 1, 2, 3], occurances)
    plt.show()
'''


def generate_random_name() -> str:
    finalName = ''
    wordCount = weighted_randint((1, 0.7), (2, 0.25), (3, 0.05))

    for wordNumber in range(wordCount):

        syllableCount = weighted_randint((1, 0.1), (2, 0.3), (3, 0.4), (4, 0.2))

        for syllable in range(syllableCount):
            # starting consonant
            if chance_boolean(0.8):
                finalName += random_from_list(consonants)
            
            # dipthong (or vowel) chance
            if chance_boolean(0.2):
                finalName += random_from_list(vowels) + random_from_list(vowels)
            else:
                finalName += random_from_list(vowels)
            
            # ending consonant pair
            for _ in range(weighted_randint((0, 0.8), (1, 0.2))):
                finalName += random_from_list(consonants)
        
        if wordNumber != wordCount-1:
            finalName += ' '
        
    # ending number
    if chance_boolean(0.2):
        finalName += f' - {str(randint(0, 15))}'


        

    # make sure our name isn't something stupid
    # if it's too short, generate a new name and return it
    if len(finalName) <= 2:
        return generate_random_name()
    else:
        return finalName.title()


