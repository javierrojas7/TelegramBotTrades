from random import randint
file = open("characters.txt","r")

characters = []
character = ""

for line in file:
    if line != ",\n":
        character += line
    else:
        characters.append(character)
        character = ""
file.close()

def rnd_character():
    return characters[randint(1, len(characters)-1)]

def starwarslogo():
    return characters[0]

def all_characters():
    return characters

def character(nr):
    return characters[nr]