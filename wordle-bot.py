# %%
import pandas as pd
import string
import re

# %%
def load_dictionary():
    words_list = []  # List to store all the words from CSV files
    for letter in list(string.ascii_uppercase):
        # Read dataframe:
        awordframe = pd.read_csv(
            f"word-library/{letter}word.csv",
            header=None,
            sep="rwerere",
            quoting=3,
            encoding="cp1252",
            engine="python",
        )
        # Remove whitespace:
        awordframe[0] = awordframe[0].str.replace(" ", "")
        # Filter to only 5-letter words
        awordframe = awordframe.loc[awordframe[0].str.len() == 5]
        # Filter to only words without punctuation:
        awordframe = awordframe.loc[awordframe[0].str.contains("^[a-z]{5}$")]
        # Filter to only unique results
        awordframe = awordframe[0].unique()
        # Append to words_list:
        words_list.extend(awordframe.tolist())
    
    # Convert list to DataFrame
    words_df = pd.DataFrame({"word": words_list})
    return words_df.reset_index(drop=True)


# %%
def find_best_letters(possible_words):
    # print("fbl plausible words:")
    # print(possible_words)
    best_letters = []
    for letter_num in [1, 2, 3, 4, 5]:
        letter_freq = possible_words.copy()
        letter_freq["word"] = letter_freq["word"].str[letter_num - 1 : letter_num]
        # print(f"df of letter {letter_num}")
        # print(letter_freq)
        letter_freq = letter_freq.groupby(["word"]).size().reset_index(name="counts")
        # letter_freq = letter_freq.loc[~letter_freq['word'].isin(best_letters)]
        # print("Letter freq:")
        # print(letter_freq)
        most_likely_letter = letter_freq.loc[letter_freq["counts"].idxmax()]["word"]
        best_letters.append(most_likely_letter)
    return best_letters


# %%
def determine_uniqueness(word):
    return len(set(word)) == 5


# %%
def rank_words_by_closeness(words, word, turn_counter):
    words["score"] = 0
    for w_no in range(len(words)):
        w = words["word"][w_no]
        score = 0
        for letternum in range(len(w)):
            if word[letternum] == w[letternum]:
                score += 1
        words.at[w_no, "score"] = score
    if turn_counter == 0:
        # Remove words with duplicate letters if first turn to eliminate more letters
        words = words.loc[
            words.apply(lambda x: determine_uniqueness(x["word"]), axis=1)
        ]
    best_ranked_word = words.loc[words["score"].idxmax()]["word"]
    return best_ranked_word


# %%
def remove_implausible_words(word, result, possible_words):
    # print("Input words:")
    # print(possible_words)
    included_letters = []
    for letterno in range(5):
        # Excludes weird cases where green letters are marked as grey
        if result[letterno] != "x":
            included_letters.append(word[letterno])
    # print("included_letters:")
    # print(included_letters)
    for letterno in range(5):
        if (result[letterno] == "x") and (word[letterno] not in included_letters):
            possible_words = possible_words.loc[
                ~(possible_words["word"].str.contains(word[letterno]))
            ]
        elif (result[letterno] == "x") and (word[letterno] in included_letters):
            possible_words = possible_words.loc[
                ~(possible_words["word"].str[letterno] == word[letterno])
            ]
        elif result[letterno] == "y":
            possible_words = possible_words.loc[
                ~(possible_words["word"].str[letterno] == word[letterno])
            ]
            possible_words = possible_words.loc[
                possible_words["word"].str.contains(word[letterno])
            ]
        elif result[letterno] == "g":
            possible_words = possible_words.loc[
                possible_words["word"].str[letterno] == word[letterno]
            ]
    possible_words = possible_words.reset_index(drop=True)
    # print("Output plausible words:")
    # print(possible_words)
    return possible_words


# %%
def score_word(word, answer):
    result = ""
    for letterno in range(5):
        if word[letterno] == answer[letterno]:
            result += "g"
        elif word[letterno] in answer:
            result += "y"
        elif word[letterno] not in answer:
            result += "x"
    return result


# %%
def play_game():
    possible_words = load_dictionary()
    win = False
    turn_counter = 0
    starting_word = "na"
    print("Choose your own starting word? y/n")
    starting_choice = input()
    while starting_choice not in ["y", "n"]:
        print("Invalid input. Choose your own starting word? y/n")
        starting_choice = input()
    if starting_choice == "y":
        print("Enter starting word:")
        starting_word = input()
        while not (
            bool(re.match("[a-z]{5}", starting_word)) and len(starting_word) == 5
        ):
            print("Invalid input. Not a 5 letter lowercase word")
            starting_word = input()
    else:
        pass
    while not win:
        if starting_choice == "n":
            best_letters = find_best_letters(possible_words)
            optimal_word = rank_words_by_closeness(
                possible_words, best_letters, turn_counter
            )
            print("Recommended word:")
            print(optimal_word)
            possible_words = possible_words.loc[
                possible_words["word"] != optimal_word
            ].reset_index(drop=True)
        else:
            optimal_word = starting_word
            possible_words = possible_words.loc[
                possible_words["word"] != optimal_word
            ].reset_index(drop=True)
            starting_choice = "n"

        print("Was word accepted? y/n")
        word_valid = input()
        while word_valid not in ["y", "n"]:
            print("Invalid input. Was word accepted? y/n")
            word_valid = input()
        if word_valid == "y":
            turn_counter += 1
            print("Did the word win? y/n")
            word_winner = input()
            while word_winner not in ["y", "n"]:
                print("Invalid input. Did the word win? y/n")
                word_winner = input()
            if word_winner == "n" and turn_counter < 6:
                print(
                    "Please enter the result: (key: x = blank, y = yellow, g = green)"
                )
                result = input()
                while not (bool(re.match("[xyg]{5}", result)) and len(result) == 5):
                    print(
                        "Invalid Input. Please enter the result: (key: x = blank, y = yellow, g = green)"
                    )
                    result = input()
            elif word_winner == "n" and turn_counter >= 6:
                print("Sorry, I couldn't guess the wordle!")
                break
            elif word_winner == "y":
                print(f"Congratulations! Won in {turn_counter} guesses!")
                win = True
                break
            possible_words = remove_implausible_words(
                optimal_word, result, possible_words
            )
            if len(possible_words) == 0:
                print("Sorry, it seems the answer isn't in my internal dictionary!")
                break
        else:
            pass


# %%
def autoplay_game(target_words):
    for answer in target_words:
        possible_words = load_dictionary()
        win = False
        turn_counter = 0
        while not win:
            best_letters = find_best_letters(possible_words)
            optimal_word = rank_words_by_closeness(
                possible_words, best_letters, turn_counter
            )
            print("Recommended word:")
            print(optimal_word)
            possible_words = possible_words.loc[
                possible_words["word"] != optimal_word
            ].reset_index(drop=True)
            # Unfortunately, it is not possible to validate whether a word is allowed when autoplaying,
            # as we do not have access to the Wordle master accepted word list.
            turn_counter += 1
            word_winner = optimal_word == answer
            if word_winner:
                print(f"Congratulations! Won in {turn_counter} guesses!")
                win = True
                break
            elif ~word_winner and turn_counter < 6:
                result = score_word(optimal_word, answer)
            elif ~word_winner and turn_counter >= 6:
                print("Sorry, I couldn't guess the wordle!")
                break
            possible_words = remove_implausible_words(
                optimal_word, result, possible_words
            )
            if len(possible_words) == 0:
                print("Sorry, it seems the answer isn't in my internal dictionary!")
                break


# %%
if __name__ == "__main__":
    play_game()
