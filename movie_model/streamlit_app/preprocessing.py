import re


# For simplicity's sake, we're removing nonenlgish movies
def contains_non_english(text):
    return not bool(re.search(r"[^\x00-\x7F]+", text))
