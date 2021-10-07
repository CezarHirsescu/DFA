/**
 * DFA Assignment in java
 */
package org.cezarhirsescu;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.exc.MismatchedInputException;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Scanner;


public class App {

    //  keeping track of states as an enum instead of as strings is more efficient,
//  since storing and equating ints is faster than storing and equating strings
    private enum State {
        word,
        deadspace,
        end_of_sentence
    }

    private static class Pair<X, Y> {
        public final X x;
        public final Y y;
        public Pair(X x, Y y) {
            this.x = x;
            this.y = y;
        }
    }


    /**
     * Uses google/s cloud translate api to translate english into another language
     * @param language the two letter name of your language (ex. french -> fr)
     * @param text the text in the original language
     * @return the text after translation
     */
    private static String translate_text(String language, String text) throws IOException {
        final String API_KEY = "AIzaSyCournbZMh2tC2J7hUfR91H7x0vBI52Chg";

        // in other languages, the json file is thought of as a dictionary (python) or object (js)
        // in java you actually have to create the json file to send it
        String json = "{\n\"q\" : \"" + text + "\",\n\"target\" : \"" + language + "\",\n}";
        FileWriter out = null;
        try {
            out = new FileWriter("file.json");
            out.write(json);
        } finally {
            if (out != null) {
                out.close();
            }
        }

        // http request
        try {
            // make the request
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("https://translation.googleapis.com/language/translate/v2?key=" + API_KEY))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofFile(Paths.get("file.json")))
                    .build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

            // parse json into object
            ObjectMapper mapper = new ObjectMapper();
            HashMap<String, HashMap<String, ArrayList<HashMap<String, String>>>> apiResponse = mapper.readValue(
                    response.body(),
                    new TypeReference<HashMap<String, HashMap<String, ArrayList<HashMap<String, String>>>>>() {});
            // get the desired information from that json object
            return apiResponse.get("data").get("translations").get(0).get("translatedText");

        } catch(FileNotFoundException | InterruptedException | MismatchedInputException e) {
            e.printStackTrace();
            System.out.println(
                    "(!) There was an error \nPerhaps when you entered your translate language you forgot to "+
                    "put it in its 2 letter form? (ex. french -> fr) \nSee this link for a list of languages: "+
                    "https://cloud.google.com/translate/docs/languages");
        }

        return "";
    }

    /**
     * This function takes in a word and potentially modifies it.
     * @param word
     * @return
     */
    private static String modifyWord(String word) {
        // corrections is a list of pairs of strings where the first string is the
        // error and the second string is the correction
        String[][] corrections = {
                // change i to I
                {"i", "I"},
                // change words with apostrophe
                {"they're", "they are"},
                {"can't", "cannot"},
                {"won't", "will not"},
                {"don't", "do not"},
                {"i've", "I have"},
                {"i'll", "I will"},
                {"i'd", "I would"},
                {"i'm", "I am"},
                {"im", "I am"},
                {"she's", "she is"},
                {"he's", "he is"},
                {"it's", "it is"},
                {"there's", "there is"},
                {"we're", "we are"},
                {"you've", "you have"},
                {"couldn't", "could not"},
                {"shouldn't", "should not"},
                {"wouldn't", "would not"},
                // 10 most common spelling mistakes
                // https://www.inc.com/melanie-curtin/the-10-most-commonly-misspelled-words-in-english-language.html
                {"accomodate", "accommodate"},
                {"wich", "which"},
                {"recieve", "receive"},
                {"untill", "until"},
                {"occured", "occurred"},
                {"seperate", "separate"},
                {"goverment", "government"},
                {"definately", "definitely"},
                {"pharoah", "pharaoh"},
                {"publically", "publicly"},
                {"the-goat", "Mr. Jimenez"}
        };
        boolean hasCapitalFirstLetter = ((word.charAt(0) >= 65) && (word.charAt(0) <= 90));
        word = word.toLowerCase();

        for (String[] correctionList : corrections) {
            if (word.equals(correctionList[0])) {
                word = correctionList[1];
                break;
            }
        }

        if (hasCapitalFirstLetter) {
            word = Character.toUpperCase(word.charAt(0)) + word.substring(1);
        }

        return word;
    }



    /**
     * The transition function is defined as "delta: state, alphabet -> state" in this wiki
     * post: https://en.wikipedia.org/wiki/Deterministic_finite_automaton .
     *
     * This function, in the mathematical sense, takes in the current state of the machine
     * such that the state is included in Q, the set of all states, and it takes in the next
     * character in the sequence, such that the character is defined in the "alphabet", the
     * set of all accepted characters.
     *
     * This function is implemented in code to take in the current state and the next character
     * and returns the next state, along with writing characters to an output file.
     *
     * This is the extended version of the transition function. This function offeres some extra
     * features, but is also slightly slower.
     *
     * The currentWord paramater is an extension of this algorithm such that it allows the program
     * to modify current words in order to "make corrections" or provide new "features" that extends
     * beyond the simple text parsing algorithm.
     *
     * This function returns the current word it is on so that it may be repeatedly passed back into
     * the function, this is better practice than having a global variable
     *
     * @param state current state of the dfa
     * @param character the next character that is read
     * @param currentWord stores the current word to make changes to it if needs correcting
     * @param writeFile the output.txt file
     * @return returns a pair of state, current word so that it can be used again
     */
    private static Pair<State, String> transition(State state, char character, String currentWord, FileWriter writeFile) throws IOException{
        character = Character.toLowerCase(character);
        int charAscii = character;
        boolean standardLetters = (
                (97 <= charAscii && charAscii <= 122) ||
                (34 <= charAscii && charAscii <= 64) ||
                (91 <= charAscii && charAscii <= 96) ||
                (123 <= charAscii && charAscii <= 126));

        if (state == State.word) {
            // if char is a sentence ending punctuation then
            // write the character and change the state to end of sentence
            // the current word will not be added on to, so write it and reset it
            if (character == '.' || character == '!' || character == '?') {
                currentWord = modifyWord(currentWord);
                writeFile.write(currentWord);
                writeFile.write(character + "  ");
                state = State.end_of_sentence;
                currentWord = "";
            }
            // if char is a space then
            // write the space and change the state to deadspace
            // the current word will not be added on to, so write it and reset it
            else if (character == ' ' || character == '\n') {
                currentWord = modifyWord(currentWord);
                writeFile.write(currentWord + " ");
                currentWord = "";
                state = State.deadspace;
            }
            // if char is a writeable symbol that is not a space or sentence ending punctuation then
            // write the char TO CURRENT WORD and don't change the state
            else if (standardLetters) {
                currentWord = currentWord + character;
            }

        } else if (state == State.deadspace) {
            // if char is a space then ignore

            // if char is a sentence ending punctuation then
            // write the char and change the state to end of sentence
            //  current word is always "" when this state is entered
            if (character == '.' || character == '!' || character == '?') {
                writeFile.write(character + "  ");
                state = State.end_of_sentence;
            }
            // if char is a writebale symbol that is not a space or sentence ending punctuation then
            // write the char TO CURRENT WORD and change the state to word
            else if (standardLetters) {
                currentWord = Character.toString(character);
                state = State.word;
            }

        } else if (state == State.end_of_sentence) {
            // if char is a sentence ending punctuation then ignore (sentence is already over)
            // if char is a space then ignore
            //
            // if char is a writebale symbol that is not a space or sentence ending punctuation then
            // write the char with a capital letter and change the state
            if (standardLetters) {
                currentWord = currentWord + Character.toUpperCase(character);
                state = State.word;
            }
        }

        return new Pair<State, String>(state, currentWord);
    }


    public static void main(String[] args) throws IOException {
        FileReader in = null;
        FileWriter out = null;

        Pair<State, String> stateStringPair = new Pair<>(State.end_of_sentence, "");

        // file io
        try {
            in = new FileReader("../input.txt");
            out = new FileWriter("../output.txt");

            int col = 0;

            int c;
            while ((c = in.read()) != -1) {
                col++;
                stateStringPair = transition(stateStringPair.x, (char) c, stateStringPair.y, out);
                // line wrap feature
                if (!stateStringPair.y.isEmpty() && col > 90) {
                    out.write('\n');
                    col = 0;
                }
            }
            // the algorithm won't know to write the last word if there is no punctuation or whitespace at
            // the end of the file. This line fixes that issue
            out.write(stateStringPair.y);

        } finally {
            // close the files
            if (in != null) {
                in.close();
            }
            if (out != null) {
                out.close();
            }
        }

        // ask the user if they want to translate the text
        Scanner scanner = new Scanner(System.in);
        System.out.println("Do you want to translate the text into another language? ([Y]/n) : ");
        String doTranslate = scanner.nextLine();
        if (doTranslate.isBlank() || Character.toLowerCase(doTranslate.charAt(0)) == 'y') {
            System.out.println(
                    "(!) You need to enter your language in its 2 letter form: " +
                            "ex. french -> fr, spanish -> es.\n" +
                            "See this link for more information: https://cloud.google.com/translate/docs/languages\n" +
                            "What language do you want to translate the text into? : "
            );

            String language = scanner.nextLine();
            StringBuilder text = new StringBuilder();
            in = null;
            try {
                in = new FileReader("../output.txt");

                int c;
                while ((c = in.read()) != -1) {
                    text.append((char) c);
                }
            } finally {
                if (in != null) {
                    in.close();
                }
            }

            String translatedText = translate_text(language, text.toString());

            if (!translatedText.isEmpty()) {
                out = null;
                try {
                    out = new FileWriter("../output.txt");
                    int col = 0;
                    for (char character : translatedText.toCharArray()) {
                        col++;
                        out.write(character);
                        // line wrap feature
                        if (!stateStringPair.y.isEmpty() && col > 90) {
                            out.write('\n');
                            col = 0;
                        }
                    }
                } finally {
                    if (out != null) {
                        out.close();
                    }
                }
            }
        }
    }
}
