# %%
import pandas as pd
import string
import re

# %%
def load_dictionary():
    words_df = pd.DataFrame({"word":pd.Series(dtype='str')})
    for letter in list(string.ascii_uppercase):
        # print(f"word-library/{letter}word.csv")
        # Read dataframe:
        awordframe = pd.read_csv(f"word-library/{letter}word.csv",header=None,sep="rwerere",quoting=3,encoding='cp1252',engine='python')
        # Remove whitespace:
        awordframe[0] = awordframe[0].str.replace(' ', '')
        # Filter to only 5-letter words
        awordframe = awordframe.loc[awordframe[0].str.len() == 5]
        # Filter to only words without punctuation:
        awordframe = awordframe.loc[awordframe[0].str.contains("[a-z]{5}")]
        # Filter to only unique results
        awordframe = awordframe[0].unique()
        # Append to words_df:
        words_df = words_df.append(pd.DataFrame({"word":awordframe}))
    words_df = words_df.reset_index(drop=True)
    return words_df

# %%
def find_best_letters(possible_words):
    best_letters = []
    for letter_num in [1,2,3,4,5]:
        letter_freq = possible_words.copy()
        letter_freq['word'] = possible_words['word'].str[letter_num-1:letter_num]
        letter_freq = letter_freq.groupby(['word']).size().reset_index(name='counts')
        letter_freq = letter_freq.loc[~letter_freq['word'].isin(best_letters)]
        most_likely_letter = letter_freq.loc[letter_freq['counts'].idxmax()]['word']
        best_letters.append(most_likely_letter)
    return best_letters

# %%
def determine_uniqueness(word):
    return len(set(word)) == 5

# %%
def rank_words_by_closeness(words,word,turn_counter):
    words['score'] = 0
    for w_no in range(len(words)):
        w = words['word'][w_no]
        score = 0
        for letternum in range(len(w)):
            if word[letternum] == w[letternum]:
                score += 1 
        words.at[w_no, 'score'] = score
    if turn_counter == 0:
        # Remove words with duplicate letters if first turn to eliminate more letters
        words = words.loc[words.apply(lambda x: determine_uniqueness(x['word']),axis=1)]
    best_ranked_word = words.loc[words['score'].idxmax()]['word']
    return best_ranked_word

# %%
def remove_implausible_words(word,result,possible_words):
    included_letters = []
    for letterno in range(5):
        # Excludes weird cases where green letters are marked as grey
        if result[letterno] != 'x':
            included_letters.append(word[letterno])
    for letterno in range(5):
        if (result[letterno] == 'x') and (word[letterno] not in included_letters):
            possible_words = possible_words[~(possible_words['word'].str.contains(word[letterno]))]
        if result[letterno] == 'y':
            possible_words = possible_words[~(possible_words['word'].str[letterno] == word[letterno])]
            possible_words = possible_words[possible_words['word'].str.contains(word[letterno])]
        if result[letterno] == 'g':
            possible_words = possible_words[possible_words['word'].str[letterno] == word[letterno]]      
    possible_words = possible_words.reset_index(drop=True)
    return possible_words

# %%
def play_game():
    possible_words = load_dictionary()
    win = False
    turn_counter = 0
    while not win:
        best_letters = find_best_letters(possible_words)
        optimal_word = rank_words_by_closeness(possible_words,best_letters,turn_counter)
        print('Recommended word:')
        print(optimal_word)
        possible_words = possible_words.loc[possible_words['word'] != optimal_word].reset_index(drop=True)
        print('Was word accepted? y/n')
        word_valid = input()
        while word_valid not in ['y','n']:
            print('Invalid input. Was word accepted? y/n')
            word_valid = input()
        if word_valid == 'y':
            turn_counter += 1
            print('Did the word win? y/n')
            word_winner = input()
            while word_winner not in ['y','n']:
                print('Invalid input. Did the word win? y/n')
                word_winner = input()
            if word_winner == 'n' and turn_counter < 6:
                print('Please enter the result: (key: x = blank, y = yellow, g = green)')
                result = input()
                while not (bool(re.match("[xyg]{5}", result)) and  len(result) == 5):
                    print('Invalid Input. Please enter the result: (key: x = blank, y = yellow, g = green)')
                    result = input()
            elif word_winner == 'n' and turn_counter >= 6:
                print("Sorry, I couldn't guess the wordle!")
                break
            elif word_winner == 'y':
                print(f"Congratulations! Won in {turn_counter} guesses!")
                win = True
                break
            possible_words = remove_implausible_words(optimal_word,result,possible_words)
        else:
            pass

# %%
if __name__ == "__main__":
    play_game()


