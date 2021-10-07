"""
DFA Assignment.

5 extra features:
    1. change i to I
    2. change words with apostrophes into their proper form
        ex. they're -> they are
    3. fix the 10 most common spelling mistakes
    4. wrap the text in the output file after 90 characters
    5. replace "The-Goat" with "Mr. Jimenez"

1 EXTRA extra feature: translate output into other languages
"""

from enum import Enum
from io import TextIOWrapper
import requests

# keeping track of states as an enum instead of as strings is more efficient,
# since storing and equating ints is faster than storing and equating strings
class States(Enum):
    word = 1
    deadspace = 2   # possible spaces in between words
    end_of_sentence = 3

# alphabet = chr(0) to chr(255)


def translate_text(language : str, text : str) -> str:
    """ 
    Uses google's cloud translate api to translate english into another language. 
    """
    try:
        print("Translating text...")
        API_KEY = "AIzaSyCournbZMh2tC2J7hUfR91H7x0vBI52Chg" 
        r = requests.post("https://translation.googleapis.com/language/translate/v2",
            params={"key" : API_KEY},
            json={
            "q" : [text],
            "target": language
        })

        result = r.json()['data']['translations'][0]['translatedText']
        print("Translation complete!")
        return result 
    except:
        print("(!) There was an error \nPerhaps when you entered your translate language you forgot to "
              "put it in its 2 letter form? (ex. french -> fr) \nSee this link for a list of languages: "
              "https://cloud.google.com/translate/docs/languages")
        return ""


def modifyWord(word : str) -> str:
    """
    This function takes in a word and potentially modifies it.
    """
    # corrections is a list of pairs of strings where the first string is the
    # error and the second string is the correction
    corrections = [
        # change i to I
        ("i", "I"),
        # change words with apostrophe
        ("they're", "they are"),
        ("can't", "cannot"),
        ("won't", "will not"),
        ("don't", "do not"),
        ("i've", "I have"),
        ("i'll", "I will"),
        ("i'd", "I would"),
        ("i'm", "I am"),
        ("im", "I am"),
        ("she's", "she is"),
        ("he's", "he is"),
        ("it's", "it is"),
        ("there's", "there is"),
        ("we're", "we are"),
        ("you've", "you have"),
        ("couldn't", "could not"),
        ("shouldn't", "should not"),
        ("wouldn't", "would not"),
        # 10 most common spelling mistakes
        # https://www.inc.com/melanie-curtin/the-10-most-commonly-misspelled-words-in-english-language.html
        ("accomodate", "accommodate"),
        ("wich", "which"),
        ("recieve", "receive"),
        ("untill", "until"),
        ("occured", "occurred"),
        ("seperate", "separate"),
        ("goverment", "government"),
        ("definately", "definitely"),
        ("pharoah", "pharaoh"),
        ("publically", "publicly"),
        ("the-goat", "Mr. Jimenez")   
    ]
    # we will remember if the word started with a capital letter
    # so that we can add the capital back on
    hasCapitalFirstLetter = 65 <= ord(word[0]) <= 90
    word = word.casefold()  

    for error, correction in corrections:
        if word == error:
            word = correction
            break
    
    if hasCapitalFirstLetter:   # replace the capital letter if it has one
        word = word[0].capitalize() + word[1:]

    return word


def transition(state : int, char : str, current_word : str, writeFile : TextIOWrapper) -> tuple :
    """
    The transition function is defined as "delta: state, alphabet -> state" in this wiki
    post: https://en.wikipedia.org/wiki/Deterministic_finite_automaton .

    This function, in the mathematical sense, takes in the current state of the machine
    such that the state is included in Q, the set of all states, and it takes in the next
    character in the sequence, such that the character is defined in the "alphabet", the 
    set of all accepted characters.

    This function is implemented in code to take in the current state and the next character
    and returns the next state, along with writing characters to an output file.

    The state paramater uses an enum to make lookups quicker, this enum is defined in the same
    file of this function. 

    This is the extended version of the transition function. This function offeres some extra
    features, but is also slightly slower.

    The currentWord paramater is an extension of this algorithm such that it allows the program
    to modify current words in order to "make corrections" or provide new "features" that extends
    beyond the simple text parsing algorithm. 
    
    This function returns the current word it is on so that it may be repeatedly passed back into
    the function, this is better practice than having a global variable
    """
    # char.casefold makes uppercase letter turn to lowercase
    char = char.casefold()
    char_ascii = ord(char)
    standardLetters = (     # all letters and symbols in the non-extended ascii set 
        (97 <= char_ascii <= 122) or 
        (34 <= char_ascii <= 64) or 
        (91 <= char_ascii <= 96) or 
        (123 <= char_ascii <= 126)
    )

    
    if state == States.word:
        # if char is a sentence ending punctuation then
        # write the character and change the state to end of sentence
        # the current word will not be added on to, so write it and reset it
        if char == '.' or char == '!' or char == '?':
            current_word = modifyWord(current_word)
            writeFile.write(current_word)
            writeFile.write(f"{char}  ")
            state = States.end_of_sentence
            current_word = ""

        # if char is a space then
        # write the space and change the state to deadspace
        # the current word will not be added on to, so write it and reset it
        elif char == ' ' or char == '\n':
            current_word = modifyWord(current_word)
            writeFile.write(current_word + " ")
            current_word = ""
            state = States.deadspace

        # if char is a writebale symbol that is not a space or sentence ending punctuation then
        # write the char TO CURRENT WORD and don't change the state
        elif (standardLetters):
            current_word = current_word + char


    elif state == States.deadspace:
        # if char is a space then ignore

        # if char is a sentence ending punctuation then
        # write the char and change the state to end of sentence
        # current word is always "" when this state is entered
        if char == '.' or char == '!' or char == '?':
            writeFile.write(f"{char}  ")
            state = States.end_of_sentence

        # if char is a writebale symbol that is not a space or sentence ending punctuation then
        # write the char TO CURRENT WORD and change the state to word
        elif (standardLetters):
            current_word = char
            state = States.word
        
    
    elif state == States.end_of_sentence:
        # if char is a sentence ending punctuation then ignore (sentence is already over)
        # if char is a space then ignore

        # if char is a writebale symbol that is not a space or sentence ending punctuation then
        # write the char with a capital letter and change the state
        if (standardLetters):
            current_word = current_word + char.capitalize()
            state = States.word

    return state, current_word


def main():
    state = States.end_of_sentence
    current_word = ""

    # file io
    with open("../input.txt", "r") as inputFile, open("../output.txt", "w") as outputFile:
        print("using extended algorithm")
        col = 0     # extra feature #4: wrap line at 90 characters
        for line in inputFile:
            for char in line:
                col += 1
                state, current_word = transition(state, char, current_word, outputFile)
                # line wrap feature
                if not current_word and col > 90:
                    outputFile.write('\n')
                    col = 0
            # the algorithm won't know to write the last word if there is no punctuation or whitespace at 
            # the end of the file. This line fixes that issue
            outputFile.write(current_word)

    # ask the user if they want to translate text
    user_input = input("Do you want to translate the text into another language? ([Y]/n) : ")
    do_translate = (not user_input or user_input[0].casefold() == 'y')
    if do_translate:
        language = input(
            "(!) You need to enter your language in its 2 letter form: "
            "ex. french -> fr, spanish -> es.\n"
            "See this link for more information: https://cloud.google.com/translate/docs/languages\n"
            "What language do you want to translate the text into? : "
        )

        text = ""

        with open("../output.txt", "r") as file:
            text = "".join(file.readlines())

        text = translate_text(language, text)
        if text:    # if text does not return empty
            with open("../output.txt", "w") as outputFile:
                col = 0
                for char in text:
                    col += 1
                    outputFile.write(char)
                    # wrap at 90 characters
                    if col > 90 and (char == ' ' or char == '?' or char == '!'):
                        outputFile.write('\n')
                        col = 0


if __name__ == "__main__":
    main()