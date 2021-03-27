import csv
import copy
import enum
import re

hidden_to_observed = {}
observed_to_hidden = {}

letter_to_tag = {  # dictionary associating letters to tags
    'Q' : "Disjunct",
    'R' : "Irrealis",
    'A' : "Aspect",
    'M' : "Modality",
    'S' : "Subject",
    'D' : "ClassifierD",
    'F' : "ClassifierS",
    'I' : "ClassifierI",
    'E' : "Epenthesis",
}

classifier_prefixes = [
    "Df{d}Ff{s}If{i}",
    "Df{d}If{i}",
    "Ff{s}If{i}",
    "Df{d}",
    "Df{d}Ff{s}",
    "Ff{s}",
    "If{i}",
    "",
]

files = [
    "verb-prefixes-02-unmarked.csv",
    "verb-prefixes-03-nconj.csv",
    "verb-prefixes-04-ghconj.csv",
    "verb-prefixes-05-gconj.csv",
    "verb-prefixes-06-perfective.csv",
    "verb-prefixes-07-prospective.csv",
]

# from StackOverflow
def sublist(ls1, ls2):
    def get_all_in(one, another):
        for element in one:
            if element in another:
                yield element

    for x1, x2 in zip(get_all_in(ls1, ls2), get_all_in(ls2, ls1)):
        if x1 != x2:
            return False

    return True
# end from StackOverflow

class SegmentSeq:
    def __init__(self, string):
        self.seq = []
        currentLetter = ''
        for (i,c) in enumerate(string):
            if c in letter_to_tag.keys():
                currentLetter = c  # get the letter representing the tag
                result = re.search("{(.*?)}", string[i:])  # get the text of the segment
                if result.group(1):
                    self.seq.append((letter_to_tag[c], result.group(1)))
    def to_string(self, hyphen=True):
        separator = "-" if hyphen else ""
        return separator.join([x[1] for x in self.seq])
    def print_verbose(self):
        for (tag, word) in self.seq:
            print(tag,word,sep="\t")
    def append(self, segment_list):
        self.seq = self.seq + segment_list
    def length(self):
        return len(self.seq)
    def same_tags(self, other):
        if self.length() != other.length():
            return False
        found_mismatch = False
        for i in range(self.length()):
            if self.seq[i][0] != other.seq[i][0]:  # compare tags
                found_mismatch = True
                break
        return not found_mismatch
    # adapted from StackOverflow
    def find_first_sublist(self, sublist, start=0):
        length = len(sublist)
        found = False
        for index in range(start, self.length()):
            if self.seq[index:index+length] == sublist:
                found = True
                break
        if found:
            return index, index+length
        return -1, -1
    def replace_sublist(self, sublist, replacement):
        length = len(replacement)
        index = 0
        start, end = self.find_first_sublist(sublist, index)
        if start != -1 or end != -1:
            self.seq[start:end] = replacement
            index = start + length
        return self
    # end from StackOverflow


for filename in files:
    f = open("csv/" + filename)
    reader = csv.reader(f)
    for line in reader:
        if line:
            for (i, prefix) in enumerate(classifier_prefixes):
                if line[4+i]:
                    if not line[3]:
                        continue
                    hidden = SegmentSeq(line[3] + classifier_prefixes[i])
                    observed = SegmentSeq(line[4+i])
                    if observed.seq:
                        if hidden in hidden_to_observed.keys():
                            print(hidden.to_string())
                        hidden_to_observed[hidden] = observed

def pair(letter, word):
    return (letter_to_tag[letter], word)


actual = [
    [pair("E", "a")],  # (1) -- remove epenthesis
    [pair("E", "a")],
    [pair("E", "a")],
    [pair("E", "a")],
    [pair("E", "o")],
    [pair("S", "x̱"), pair("A", "w")],
    # Irrealis w/u
    [pair("A", "k"), pair("R", "w")],
    [pair("M", "g̱"), pair("R", "w")],  # (H)
    [pair("F", "s")],  # (C)
    [pair("R", "u"), pair("M", "g̱")],  # Undo (H)
    [pair("D", "d"), pair("F", "s")],  # Undo (C)
    # [pair("A", "g̱")],
    [pair("A", "g̱"), pair("R", "w")],
    # Modal g̱
    [pair("M", "x̱")],
    [pair("A", "k"), pair("M", "g̱")],
    [pair("A", "g"), pair("M", "g̱")],  # (A)
    [pair("A", "g"), pair("R", "u"), pair("M", "g̱")],
    [pair("A", "k"), pair("S", "ḵ"), pair("R", "w")],
    [pair("A", "g"), pair("M", "g̱"), pair("R", "w")],
    [pair("A", "k"), pair("R", "u"), pair("S", "ḵ")],
    [pair("A", "k"), pair("S", "ḵ")],
    [pair("A", "g"), pair("S", "ḵ")],
    [pair("A", "ḵ"), pair("S", "ḵ")],
    [pair("A", "ḵ"), pair("R", "w"), pair("S", "ḵ")],
    [pair("A", "g̱"), pair("R", "w"), pair("M", "g̱")],
    [pair("A", "g"), pair("R", "o"), pair("S", "ḵ")],
    [pair("A", "g"), pair("R", "o")],
    [pair("A", "g̱"), pair("M", "g̱")],
    # Subject du
    [pair("A", "k"), pair("S", "du")],
    [pair("A", "g"), pair("S", "du")],
    [pair("A", "x̱"), pair("S", "du")],
    [pair("A", "g̱"), pair("S", "du")],
    # Subject i
    [pair("S", "y")],
    [pair("A", "g"), pair("S", "i")],
    [pair("A", "g"), pair("S", "ee")],
    [pair("A", "g"), pair("S", "yi")],
    [pair("A", "g"), pair("S", "yee")],
    [pair("A", "x̱"), pair("S", "yi")],
    [pair("A", "x̱"), pair("S", "ye")],
    [pair("A", "g̱"), pair("S", "yi")],
    [pair("A", "g̱"), pair("S", "ye")],
    [pair("A", "g̱"), pair("S", "i")],
    [pair("A", "g̱"), pair("S", "ee")],
    # Subject tu
    [pair("A", "k"), pair("S", "tu")],
    [pair("A", "k"), pair("S", "too")],
    [pair("A", "g"), pair("S", "tu")],
    [pair("A", "g"), pair("S", "too")],  # (D)
    [pair("A", "x̱"), pair("S", "too")],
    [pair("A", "x̱"), pair("S", "tu")],
    [pair("A", "g̱"), pair("S", "tu")],
    [pair("A", "g̱"), pair("S", "too")],
    # Subject x̱
    [pair("S", "ḵ"), pair("R", "w")],
    [pair("S", "ḵ")],
    [pair("A", "g̱"), pair("S", "x̱")], # (G)
    # [pair("R", "e"), pair("S", "ḵ")],
    # [pair("R", "o"), pair("S", "ḵ")],
    # [pair("R", "i"), pair("S", "ḵ")],
    # [pair("S", "ḵ"), pair("R", "w")],
    # Aspect wu
    [pair("Q", "a"), pair("S", "i")],
    [pair("Q", "ka"), pair("S", "i")],
    [pair("Q", "x̱ʼa"), pair("S", "i")],
    [pair("Q", "ji"), pair("S", "i")],
    [pair("Q", "tu"), pair("S", "i")],
    [pair("A", "e"), pair("S", "e")],
    # Aspect n
    [pair("F", "s")],  # (C)
    [pair("D", "d"), pair("F", "s")],  # Undo (C)
    [pair("A", "n")],
    [pair("A", "n"), pair("A", "g̱")],
    [pair("F", "s")],  # (C)
    [pair("D", "d"), pair("F", "s")],  # Undo (C)
    [pair("A", "n"), pair("S", "yi")],
    [pair("A", "n"), pair("S", "du")],
    # ClassifierD
    [pair("F", "s")],  # (C)
    # Undo errors
    [pair("R", "w"), pair("A", "g"), pair("M", "g̱")],  # Undo (A)
    [pair("R", "o"), pair("R", "u")],  # Undo irrealis
    [pair("R", "u"), pair("R", "u")],
    [pair("R", "e"), pair("R", "u")],
    [pair("R", "i"), pair("R", "u")],
    [pair("R", "u"), pair("A", "n")],
    [pair("R", "u"), pair("A", "g")],
    [pair("R", "u"), pair("A", "g̱")],
    [pair("M", "g̱")],  # (F)
    [pair("D", "d"), pair("F", "s")],  # Undo (C)
    [pair("R", "u"), pair("M", "g̱")],  # (F)
    [pair("M", "g̱"), pair("S", "x̱")],  # Undo (G)
    [pair("F", "s")],  # (C)
]
rewritten = [
    [],
    [],
    [],
    [],
    [],
    [pair("A", "wu"), pair("S", "x̱")],
    # Irrealis w/u
    [pair("R", "u"), pair("A", "g")],
    [pair("R", "u"), pair("M", "g̱")],  # (H)
    [pair("D", "d"), pair("F", "s")],  # (C)
    [pair("M", "g̱"), pair("R", "w")],  # Undo (H)
    [pair("F", "s")],  # Undo (C)
    # [pair("R", "u"), pair("A", "g̱")],
    [pair("R", "u"), pair("A", "g̱")],
    # Modal g̱
    [pair("M", "g̱")],
    [pair("A", "g"), pair("M", "g̱")],
    [pair("R", "w"), pair("A", "g"), pair("M", "g̱")],  # (A)
    [pair("R", "w"), pair("A", "g"), pair("M", "g̱")],
    [pair("R", "w"), pair("A", "g"), pair("M", "g̱"), pair("S", "x̱")],
    [pair("A", "g"), pair("M", "g̱")],
    [pair("R", "w"), pair("A", "g"), pair("M", "g̱"), pair("S", "x̱")],
    [pair("A", "g"), pair("M", "g̱"), pair("S", "x̱")],
    [pair("A", "g"), pair("M", "g̱"), pair("S", "x̱")],
    [pair("A", "g̱"), pair("M", "g̱"), pair("S", "x̱")],
    [pair("R", "u"), pair("A", "g̱"), pair("M", "g̱"), pair("S", "x̱")],
    [pair("R", "u"), pair("A", "g̱"), pair("M", "g̱")],
    [pair("R", "u"), pair("A", "g"), pair("M", "g̱"), pair("S", "x̱")],
    [pair("R", "u"), pair("A", "g")],
    [pair("R", "u"), pair("A", "g̱"), pair("M", "g̱")],
    # Subject du
    [pair("R", "u"), pair("A", "g"), pair("S", "du")],
    [pair("R", "u"), pair("A", "g"), pair("S", "du")],  # (B)
    [pair("R", "u"), pair("A", "g̱"), pair("S", "du")],
    [pair("R", "u"), pair("A", "g̱"), pair("S", "du")],
    # Subject i
    [pair("S", "i")],
    [pair("R", "u"), pair("A", "g"), pair("S", "i")],
    [pair("R", "u"), pair("A", "g"), pair("S", "i")],
    [pair("R", "u"), pair("A", "g"), pair("S", "yi")],
    [pair("R", "u"), pair("A", "g"), pair("S", "yi")],  # (E)
    [pair("R", "u"), pair("A", "g̱"), pair("S", "yi")],
    [pair("R", "u"), pair("A", "g̱"), pair("S", "yi")],
    [pair("R", "u"), pair("A", "g̱"), pair("S", "yi")],
    [pair("R", "u"), pair("A", "g̱"), pair("S", "yi")],
    [pair("R", "u"), pair("A", "g̱"), pair("S", "yi")],
    [pair("R", "u"), pair("A", "g̱"), pair("S", "yi")],
    # Subject tu
    [pair("R", "u"), pair("A", "g"), pair("S", "tu")],
    [pair("R", "u"), pair("A", "g"), pair("S", "tu")],
    [pair("R", "u"), pair("A", "g"), pair("S", "tu")],
    [pair("R", "u"), pair("A", "g"), pair("S", "tu")],  # (D)
    [pair("R", "u"), pair("A", "g̱"), pair("S", "tu")],
    [pair("R", "u"), pair("A", "g̱"), pair("S", "tu")],
    [pair("R", "u"), pair("A", "g̱"), pair("S", "tu")],
    [pair("R", "u"), pair("A", "g̱"), pair("S", "tu")],
    # Subject x̱
    [pair("R", "u"), pair("S", "ḵ")],
    [pair("A", "g̱"), pair("S", "x̱")],
    [pair("M", "g̱"), pair("S", "x̱")],  # (G)
    # [pair("R", "u"), pair("A", "g̱"), pair("S", "x̱")],
    # [pair("R", "u"), pair("A", "g̱"), pair("S", "x̱")],
    # [pair("R", "u"), pair("A", "g̱"), pair("S", "x̱")],
    # [pair("R", "u"), pair("A", "g̱"), pair("S", "x̱")],
    # Aspect wu
    [pair("Q", "a"), pair("A", "wu"), pair("S", "i")],
    [pair("Q", "ka"), pair("A", "wu"), pair("S", "i")],
    [pair("Q", "x̱ʼe"), pair("A", "wu"), pair("S", "i")],
    [pair("Q", "ji"), pair("A", "wu"), pair("S", "i")],
    [pair("Q", "tu"), pair("A", "wu"), pair("S", "i")],
    [pair("Q", "a"), pair("A", "wu"), pair("S", "i")],
    # Aspect n
    [pair("D", "d"), pair("F", "s")],  # (C)
    [pair("F", "s")],  # Undo (C)
    [pair("R", "u"), pair("A", "n")],
    [pair("A", "n"), pair("M", "g̱")],
    [pair("D", "d"), pair("F", "s")],  # (C)
    [pair("F", "s")],  # Undo (C)
    [pair("A", "n"), pair("M", "g̱"), pair("S", "yi")],
    [pair("A", "n"), pair("M", "g̱"), pair("S", "du")],
    # ClassifierD
    [pair("D", "d"), pair("F", "s")],  # (C)
    # Undo errors
    [pair("A", "g"), pair("M", "g̱")],  # Undo (A)
    [pair("R", "u")],  # Undo irrealis
    [pair("R", "u")],
    [pair("R", "u")],
    [pair("R", "u")],
    [pair("A", "n")],
    [pair("A", "g")],
    [pair("A", "g̱")],
    [pair("R", "u"), pair("M", "g̱")],  # (F)
    [pair("F", "s")],  # Undo (C)
    [pair("M", "g̱")],  # Undo (F)
    [pair("A", "g̱"), pair("S", "x̱")], # Undo (G)
    [pair("D", "d"), pair("F", "s")],  # (C)
    # Irrealis-subject
]

def pair_list_to_string(pair_list):
    ret_val = ""
    for pair in pair_list:
        ret_val += pair[1]
    return ret_val

actual_to_rewritten = {}
for k in hidden_to_observed.keys():
    actual_to_rewritten[hidden_to_observed[k]] = copy.deepcopy(hidden_to_observed[k])
# count = 0
# 
# for v in hidden_to_observed.values():
#     observed_to_hidden[v.to_string(False)] = set()
# for (k,v) in hidden_to_observed.items():
#     observed_to_hidden[v.to_string(False)].add(k.to_string(True))
# count = 0
# for (k,v) in observed_to_hidden.items():
#     if len(v) != 1:
#         count += 1
#         print(k,v)
# print(count)

print("So far:", len(observed_to_hidden), "\t", "Rest:", len(hidden_to_observed))
def remove_matching_tags():
    count = 0
    to_be_deleted = set()
    for (k,v) in hidden_to_observed.items():
        if k.same_tags(actual_to_rewritten[v]):
            name = v.to_string(False)
            if not name in observed_to_hidden.keys():
                observed_to_hidden[name] = set()
            observed_to_hidden[name].add(k)
            to_be_deleted.add(k)
            count += 1
    print(len(to_be_deleted))
    for k in to_be_deleted:
        hidden_to_observed.pop(k, None)
        # print(k.to_string(True), v.to_string(True), v.to_string(False), sep="    ")

remove_matching_tags()
print("So far:", len(observed_to_hidden), "\t", "Rest:", len(hidden_to_observed))
for i in range(len(actual)):
    for (k,v) in actual_to_rewritten.items():
        actual_to_rewritten[k] = v.replace_sublist(actual[i], rewritten[i])
    print(pair_list_to_string(actual[i]), "->", pair_list_to_string(rewritten[i]), ": removed", end=" ")
    remove_matching_tags()
    print("So far:", len(observed_to_hidden), "\t", "Rest:", len(hidden_to_observed))

for (k,v) in observed_to_hidden.items():
    pass
    # print(k, "\t", list(x.to_string() for x in v))
for (k,v) in hidden_to_observed.items():
    pass
    # print(k.print_verbose(), print(), actual_to_rewritten[v].print_verbose(), v.to_string(False), sep="    ")
    # print(k.to_string(True), actual_to_rewritten[v].to_string(True), v.to_string(False), sep="    ")
