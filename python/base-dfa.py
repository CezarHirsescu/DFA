from io import TextIOWrapper
from dfa import States

def transition(state : int, char : str, writeFile : TextIOWrapper) -> int :
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
    """
    # char.casefold makes uppercase letter turn to lowercase
    char = char.casefold()
    char_ascii = ord(char)

    if state == States.word:
        # if char is a sentence ending punctuation then
        # write the character and change the state to end of sentence
        if char == '.' or char == '!' or char == '?':
            writeFile.write(f"{char}  ")
            state = States.end_of_sentence

        # if char is a space then
        # write the space and change the state to deadspace
        elif char == ' ' or char == '\n':
            writeFile.write(" ")
            state = States.deadspace

        # if char is a writebale symbol that is not a space or sentence ending punctuation then
        # write the char and don't change the state
        elif (
            # all letters and symbols in the non-extended ascii set 
            (97 <= char_ascii <= 122) or 
            (34 <= char_ascii <= 64) or 
            (91 <= char_ascii <= 96) or 
            (123 <= char_ascii <= 126)
        ):
            writeFile.write(char)


    elif state == States.deadspace:
        # if char is a space then ignore

        # if char is a sentence ending punctuation then
        # write the char and change the state to end of sentence
        if char == '.' or char == '!' or char == '?':
            writeFile.write(f"{char}  ")
            state = States.end_of_sentence

        # if char is a writebale symbol that is not a space or sentence ending punctuation then
        # write the char and change the state to word
        elif (
            # all letters and symbols in the non-extended ascii set 
            (97 <= char_ascii <= 122) or 
            (34 <= char_ascii <= 64) or 
            (91 <= char_ascii <= 96) or 
            (123 <= char_ascii <= 126)
        ):
            writeFile.write(char)
            state = States.word
        
    
    elif state == States.end_of_sentence:
        # if char is a sentence ending punctuation then ignore (sentence is already over)
        # if char is a space then ignore

        # if char is a writebale symbol that is not a space or sentence ending punctuation then
        # write the char with a capital letter and change the state
        if (
            # all letters and symbols in the non-extended ascii set 
            (97 <= char_ascii <= 122) or 
            (34 <= char_ascii <= 64) or 
            (91 <= char_ascii <= 96) or 
            (123 <= char_ascii <= 126)
        ):
            writeFile.write(char.capitalize())
            state = States.word

    return state

def main():
    state = States.end_of_sentence
    # file io
    with open("input.txt", "r") as inputFile, open("output.txt", "w") as outputFile:
        print("using base algorithm")
        for line in inputFile:
            for char in line:
                state = transition(state, char, outputFile)


if __name__ == "__main__":
    main()