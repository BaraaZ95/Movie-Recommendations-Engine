from typing import List
from ast import literal_eval
import re
import string


# def text_preprocessing(column):
#    from nltk.corpus import stopwords
#
#    # Stopwords help us to get rid of unwanted words like: a, an, are, is, ...
#    stop = stopwords.words("english")
#    # make all words with lower letters
#    column = column.str.lower()
#    # getting rid of any punctution
#    column = column.str.replace("http\S+|www.\S+|@|%|:|,|", "", case=False)
#    # spliting each sentence to words to apply previous funtions on them
#    word_tokens = column.str.split()
#    keywords = word_tokens.apply(lambda x: [item for item in x if item not in stop])
#    # assemble words of each sentence again and assign them in new column
#    for i in range(len(keywords)):
#        keywords[i] = " ".join(keywords[i])
#        column = keywords
#
#    return column


# Captures the values from the dict keys from a string of list of dicts
def convert_str_to_list(obj: str, key: str, limit: int) -> List[str]:
    List_ = [i[key] for i in literal_eval(obj)]
    if (
        limit
    ):  # If limit specified, slice the list and take a limited number of elements
        return List_[:limit]
    else:
        return List_


def get_text(text, obj="name"):
    text = literal_eval(text)

    if len(text) == 1:
        for i in text:
            return i[obj]
    else:
        s = []
        for i in text:
            s.append(i[obj])
        return ", ".join(s)


def separate(text):
    clean_text = []
    for t in text.split(","):
        cleaned = re.sub("\(.*\)", "", t)  # type: ignore
        cleaned = cleaned.translate(str.maketrans("", "", string.digits))
        cleaned = cleaned.replace(" ", "")
        cleaned = cleaned.translate(str.maketrans("", "", string.punctuation)).lower()
        clean_text.append(cleaned)
    return " ".join(clean_text)


def remove_punctuation(text):
    cleaned = text.translate(str.maketrans("", "", string.punctuation)).lower()
    clean_text = cleaned.translate(str.maketrans("", "", string.digits))
    return clean_text
