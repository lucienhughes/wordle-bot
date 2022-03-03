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
        awordframe = pd.read_csv(f"word-library/{letter}word.csv",header=None,sep="rwerere",quoting=3,encoding='cp1252')
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
def rank_words_by_closeness(possible_words,word):
    possible_words['score'] = 0
    for w_no in range(len(possible_words)):
        w = possible_words['word'][w_no]
        score = 0
        for letternum in range(len(w)):
            if word[letternum] == w[letternum]:
                score += 1 
        possible_words.at[w_no, 'score'] = score
    best_ranked_word = possible_words.loc[possible_words['score'].idxmax()]['word']
    return best_ranked_word

# %%
def remove_implausible_words(possible_words,result):
    for letterno in range(5):
        if result[letterno] == 'x':
            possible_worlds = possible_words[~(possible_words['word'].str.contains(word[letterno]))]
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
    while not win:
        best_letters = find_best_letters(possible_words)
        optimal_word = rank_words_by_closeness(possible_words,best_letters)
        print('Recommended word:')
        print(optimal_word)
        possible_words = possible_words.loc[possible_words['word'] != optimal_word].reset_index(drop=True)
        print('Was word accepted? y/n')
        word_valid = input()
        while word_valid not in ['y','n']:
            print('Invalid input. Was word accepted? y/n')
            word_valid = input()
        if word_valid == 'y':
            print('Please enter the result: (key: x = blank, y = yellow, g = green)')
            result = input()
            while not (bool(re.match("[xyg]{5}", result)) and  len(result) == 5):
                print('Invalid Input. Please enter the result: (key: x = blank, y = yellow, g = green)')
                result = input()
            possible_words = remove_implausible_words(possible_words,result)
        else:
            pass

# %%
if __name__ == "__main__":
    play_game()

