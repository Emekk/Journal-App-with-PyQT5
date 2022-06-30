from collections import Counter
import pathlib
import json

# settings
path = pathlib.Path("./Journals/jrn_emek.json")
to_remove = ["<textarea>", "</textarea>", "<br>"]
to_blank = [',', '.', '(', ')', '/']

# read journal
jrn_dict = {}
with open(path, 'r') as f:
    jrn_dict = json.load(f)

# analyse
all_entries = ""
for entry_list in jrn_dict.values():
    for entry in entry_list:
        entry_text = entry[0]
        for elem in to_remove:
            entry_text = entry_text.replace(elem, '')
        all_entries += entry_text


for char in to_blank:
    all_entries = all_entries.replace(char, ' ')
words = all_entries.lower().split()
counter_word = Counter(words)

for k, v in counter_word.most_common():
    print(f"{k}: {v}")