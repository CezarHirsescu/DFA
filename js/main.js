/*
DFA Assignment.

5 extra features:
    1. change i to I
    2. change words with apostrophes into their proper form
        ex. they're -> they are
    3. fix the 10 most common spelling mistakes
    4. wrap the text in the output file after 90 characters
    5. replace "The-Goat" with "Mr. Jimenez"

1 EXTRA extra feature: translate output into other languages
 */

import fetch from "node-fetch"
import fs from "fs"
// this allows for user input in the console in node.js
// node.js is the runtime environment that I'm using to run this javascript file
import promptSync from "prompt-sync"
const prompt = promptSync({ sigint: true })
// keeping track of states as an enum instead of as strings is more efficient,
// since storing and equating ints is faster than storing and equating strings
const States = {
	word: 1,
	deadspace: 2,
	end_of_sentance: 3,
}

// alphabet = chr(0) to chr(255)

/**
 * Uses google's cloud translate api to translate english into another language.
 * This function is asyncronus because it is making an api call
 * @param {String} language
 * @param {String} text
 * @retruns {String}
 */
async function translate_text(language, text) {
	try {
		const API_KEY = "AIzaSyCournbZMh2tC2J7hUfR91H7x0vBI52Chg"
		const url = `https://translation.googleapis.com/language/translate/v2?key=${API_KEY}`
		const options = {
			method: "POST",
			headers: {
				Accept: "application/json",
				"Content-Type": "application/json;charset=UTF-8",
			},
			body: JSON.stringify({
				q: [text],
				source: "en",
				target: language,
				format: "text",
			}),
		}
		const r = await fetch(url, options)
		const data = await r.json()
		const translatedText = data["data"]["translations"][0]["translatedText"]
		return translatedText
	} catch (error) {
		console.error(error)
		console.log(
			"(!) There was an error \nPerhaps when you entered your translate language you forgot to " +
				"put it in its 2 letter form? (ex. french -> fr) \nSee this link for a list of languages: " +
				"https://cloud.google.com/translate/docs/languages"
		)
		return ""
	}
}

/**
 * This function takes in a word and potentially modifies it.
 * @param {String} word
 * @returns {String}
 */
function modifyWord(word) {
	// corrections is a list of pairs of strings where the first string is the
	// error and the second string is the correction
	const corrections = [
		// change i to I
		["i", "I"],
		// change words with apostrophe
		["they're", "they are"],
		["can't", "cannot"],
		["won't", "will not"],
		["don't", "do not"],
		["i've", "I have"],
		["i'll", "I will"],
		["i'd", "I would"],
		["i'm", "I am"],
		["im", "I am"],
		["she's", "she is"],
		["he's", "he is"],
		["it's", "it is"],
		["there's", "there is"],
		["we're", "we are"],
		["you've", "you have"],
		["couldn't", "could not"],
		["shouldn't", "should not"],
		["wouldn't", "would not"],
		// 10 most common spelling mistakes
		// https://www.inc.com/melanie-curtin/the-10-most-commonly-misspelled-words-in-english-language.html
		["accomodate", "accommodate"],
		["wich", "which"],
		["recieve", "receive"],
		["untill", "until"],
		["occured", "occurred"],
		["seperate", "separate"],
		["goverment", "government"],
		["definately", "definitely"],
		["pharoah", "pharaoh"],
		["publically", "publicly"],
		["the-goat", "Mr. Jimenez"],
	]
	// we will remember if the word started with a capital letter
	// so that we can add the capital back on
	const hasCapitalFirstLetter =
		65 <= word.charCodeAt(0) && word.charCodeAt(0) <= 90
	word = word.toLowerCase()

	corrections.forEach(([error, correction]) => {
		if (word === error) {
			word = correction
			return
		}
	})

	if (hasCapitalFirstLetter) {
		word = word.charAt(0).toUpperCase() + word.slice(1)
	}

	return word
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
 * The js version has a small modification, instead of passing the file this function is
 * going to pass a large string, which when finished will be written to the output file
 *
 * @param {Number} state
 * @param {String} char
 * @param {String} currentWord
 * @param {String} outputText
 */
function transition(state, char, currentWord, outputText) {
	char = char.toLowerCase()
	const charAscii = char.charCodeAt(0)
	const standardLetters = // all letters and symbols in the non-extended ascii set
		(97 <= charAscii && charAscii <= 122) ||
		(34 <= charAscii && charAscii <= 64) ||
		(91 <= charAscii && charAscii <= 96) ||
		(123 <= charAscii && charAscii <= 126)

	if (state == States.word) {
		// if char is a sentence ending punctuation then
		// write the character and change the state to end of sentence
		// the current word will not be added on to, so write it and reset it
		if (char === "." || char === "!" || char === "?") {
			currentWord = modifyWord(currentWord)
			outputText += currentWord
			outputText += char + "  "
			state = States.end_of_sentance
			currentWord = ""
		}
		// if char is a space then
		// write the space and change the state to deadspace
		// the current word will not be added on to, so write it and reset it
		else if (char === " " || char === "\n") {
			currentWord = modifyWord(currentWord)
			outputText += currentWord + " "
			currentWord = ""
			state = States.deadspace
		}
		// if char is a writebale symbol that is not a space or sentence ending punctuation then
		// write the char TO CURRENT WORD and don't change the state
		else if (standardLetters) {
			currentWord += char
		}
	} else if (state === States.deadspace) {
		// if char is a space then ignore

		// if char is a sentence ending punctuation then
		// write the char and change the state to end of sentence
		// current word is always "" when this state is entered
		if (char == "." || char == "!" || char == "?") {
			outputText += char + "  "
			state = States.end_of_sentance
		}
		// if char is a writebale symbol that is not a space or sentence ending punctuation then
		// write the char TO CURRENT WORD and change the state to word
		else if (standardLetters) {
			currentWord = char
			state = States.word
		}
	} else if (state === States.end_of_sentance) {
		// if char is a sentence ending punctuation then ignore (sentence is already over)
		// if char is a space then ignore

		// if char is a writebale symbol that is not a space or sentence ending punctuation then
		// write the char with a capital letter and change the state
		if (standardLetters) {
			currentWord += char.toUpperCase()
			state = States.word
		}
	}

	return [state, currentWord, outputText]
}

function main() {
	let state = States.end_of_sentance
	let currentWord = ""
	let outputText = ""
	let col = 0

	// file io
	fs.readFile("../input.txt", "utf8", (err, data) => {
		if (err) {
			console.error(err)
			return
		}
		data.split("").forEach((char) => {
			col++
			;[state, currentWord, outputText] = transition(
				state,
				char,
				currentWord,
				outputText
			)
			if (col > 90) {
				outputText += "\n"
				col = 0
			}
		})
		// the algorithm won't know to write the last word if there is no punctuation or whitespace at
		// the end of the file. This line fixes that issue
		outputText += currentWord
		fs.writeFile("../output.txt", outputText, (err) => {
			if (err) {
				console.error(err)
				return
			}
		})
	})

	// ask the user if they want to translate text
	const doTranslate = prompt("Do you want to translate the text into another language? ([Y]/n) : ")
	if (doTranslate === "" || doTranslate.charAt(0).toLowerCase() == "y") {
		const language = prompt(
			"(!) You need to enter your language in its 2 letter form: " +
				"ex. french -> fr, spanish -> es.\n" +
				"See this link for more information: https://cloud.google.com/translate/docs/languages\n" +
				"What language do you want to translate the text into? : "
		)

		fs.readFile("../output.txt", "utf8", (err, text) => {
			if (err) {
				console.error(err)
				return
			}
            // translate_text returns a promise because it is making an api call
            // so I need to use a .then to do something with the resul
			translate_text(language, text).then((translatedText) => {
				if (translatedText) {
					fs.writeFile("../output.txt", translatedText, (err) => {
						if (err) {
							console.error(err)
							return
						}
					})
				}
			})
		})
	}
}

main()
