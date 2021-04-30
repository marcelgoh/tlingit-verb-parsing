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

def p(letter, word):
    return (letter_to_tag[letter], word)

rewrites = []

def remove_epenthesis():  # (i)
    rewrites.extend([
        ([p("E", "a")],                                 []),
        ([p("E", "a")],                                 []),
        ([p("E", "a")],                                 []),
        ([p("E", "a")],                                 []),
        ([p("E", "o")],                                 []),
        ([p("E", "i")],                                 []),
    ])

def irreg_disjuncts():  # (ii)
    rewrites.extend([
        ([p("Q", "e")],                                 [p("Q", "a")]),
        ([p("Q", "k")],                                 [p("Q", "ka")]),
        ([p("Q", "x̱ʼ")],                                [p("Q", "x̱ʼe")]),
        ([p("Q", "j")],                                 [p("Q", "ji")]),
        ([p("Q", "t")],                                 [p("Q", "tu")]),
    ])

def xw2wux():  # (iii) covers both irrealis and aspect
    rewrites.extend([
        ([p("S", "x̱"), p("A", "w")],                    [p("A", "wu"), p("S", "x̱")]),
        ([p("S", "x̱"), p("R", "w")],                    [p("R", "u"), p("S", "x̱")]),
        ([p("S", "ḵ"), p("R", "w")],                    [p("R", "u"), p("S", "ḵ")]),
    ])

def make_RuAg():  # (iv)
    rewrites.extend([
        ([p("A", "k"), p("R", "w")],                    [p("R", "u"), p("A", "g")]),
        ([p("A", "g̱"), p("R", "w")],                    [p("R", "u"), p("A", "g̱")]),
    ])

def gw2ug():  # (v)
    rewrites.extend([
        ([p("M", "g̱"), p("R", "w")],                    [p("R", "u"), p("M", "g̱")]),  # (H)
    ])

def gw2ug_inv():  # (v)^-1
    rewrites.extend([
        ([p("R", "u"), p("M", "g̱")],                    [p("M", "g̱"), p("R", "w")]),  # Undo (H)
    ])

def s2ds():  # (vi)
    rewrites.extend([
        ([p("F", "s")],                                 [p("D", "d"), p("F", "s")]),  # (C)
    ])

def s2ds_inv():  # (vi)^-1
    rewrites.extend([
        ([p("D", "d"), p("F", "s")],                    [p("F", "s")]),  # Undo (C)
    ])

def Mx2Mg():  # (vii)
    rewrites.extend([
        ([p("M", "x̱")],                                 [p("M", "g̱")]),
        ([p("A", "k"), p("M", "g̱")],                    [p("A", "g"), p("M", "g̱")]),
    ])

def make_AgMg():  # (viii)
    rewrites.extend([
        ([p("A", "g"), p("M", "g̱"), p("R", "w")],       [p("A", "g"), p("M", "g̱")]),
        ([p("A", "g"), p("R", "u"), p("M", "g̱")],       [p("A", "g"), p("M", "g̱")]),
        ([p("A", "g̱"), p("R", "w"), p("M", "g̱")],       [p("A", "g̱"), p("M", "g̱")]),
    ])

def gg2wgg():  # (ix) invertible??
    rewrites.extend([
        ([p("A", "g"), p("M", "g̱")],                    [p("R", "w"), p("A", "g"), p("M", "g̱")]),  # (A)
        ([p("A", "g̱"), p("M", "g̱")],                    [p("R", "u"), p("A", "g̱"), p("M", "g̱")]),
    ])

def gg2wgg_inv():  # (ix)^-1
    rewrites.extend([
        ([p("R", "u"), p("A", "g̱"), p("M", "g̱")],       [p("A", "g̱"), p("M", "g̱")]),  # Undo (A)
        ([p("R", "w"), p("A", "g"), p("M", "g̱")],       [p("A", "g"), p("M", "g̱")]),  # Undo (A)
    ])

def make_wggx():  # (x)
    rewrites.extend([
        ([p("A", "k"), p("S", "ḵ"), p("R", "w")],       [p("R", "w"), p("A", "g"), p("M", "g̱"), p("S", "x̱")]),
        ([p("A", "k"), p("R", "u"), p("S", "ḵ")],       [p("R", "u"), p("A", "g"), p("M", "g̱"), p("S", "x̱")]),
        ([p("A", "ḵ"), p("R", "w"), p("S", "ḵ")],       [p("R", "w"), p("A", "g̱"), p("M", "g̱"), p("S", "x̱")]),
    ])

def make_ggx():  # (xi)
    rewrites.extend([
        ([p("A", "k"), p("S", "ḵ")],                    [p("A", "g"), p("M", "g̱"), p("S", "x̱")]),
        ([p("A", "g"), p("S", "ḵ")],                    [p("A", "g"), p("M", "g̱"), p("S", "x̱")]),
        ([p("A", "ḵ"), p("S", "ḵ")],                    [p("A", "g̱"), p("M", "g̱"), p("S", "x̱")]),
    ])

def go2ug():  # (xii)
    rewrites.extend([
        ([p("A", "g"), p("R", "o")],                    [p("R", "u"), p("A", "g")]),
    ])

def irreg_subj():  # (xiii)
    rewrites.extend([
        ([p("S", "y")],                                 [p("S", "i")]),
        ([p("S", "ee")],                                [p("S", "i")]),
        ([p("S", "yee")],                               [p("S", "yi")]),
        ([p("S", "ye")],                                [p("S", "yi")]),
        ([p("S", "too")],                               [p("S", "tu")]),
        ([p("S", "ḵ")],                                 [p("A", "g̱"), p("S", "x̱")]),
    ])

def make_ugdu():  # (xiv)
    rewrites.extend([
        ([p("A", "k"), p("S", "du")],                   [p("R", "u"), p("A", "g"), p("S", "du")]),
        ([p("A", "g"), p("S", "du")],                   [p("R", "u"), p("A", "g"), p("S", "du")]),  # (B)
        ([p("A", "x̱"), p("S", "du")],                   [p("R", "u"), p("A", "g̱"), p("S", "du")]),
        ([p("A", "g̱"), p("S", "du")],                   [p("R", "u"), p("A", "g̱"), p("S", "du")]),
    ])

def make_ugi():  # (xv)
    rewrites.extend([
        ([p("A", "g"), p("S", "i")],                    [p("R", "u"), p("A", "g"), p("S", "i")]),
    ])

def make_ugyi():  # (xvi)
    rewrites.extend([
        ([p("A", "g"), p("S", "yi")],                   [p("R", "u"), p("A", "g"), p("S", "yi")]),
        ([p("A", "x̱"), p("S", "yi")],                   [p("R", "u"), p("A", "g̱"), p("S", "yi")]),
        ([p("A", "g̱"), p("S", "yi")],                   [p("R", "u"), p("A", "g̱"), p("S", "yi")]),
        ([p("A", "g̱"), p("S", "i")],                    [p("R", "u"), p("A", "g̱"), p("S", "yi")]),
        ([p("A", "g̱"), p("S", "ee")],                   [p("R", "u"), p("A", "g̱"), p("S", "yi")]),
    ])

def make_ugtu():  # (xvii)
    rewrites.extend([
        ([p("A", "k"), p("S", "tu")],                   [p("R", "u"), p("A", "g"), p("S", "tu")]),
        ([p("A", "g"), p("S", "tu")],                   [p("R", "u"), p("A", "g"), p("S", "tu")]),
        ([p("A", "x̱"), p("S", "tu")],                   [p("R", "u"), p("A", "g̱"), p("S", "tu")]),
        ([p("A", "g̱"), p("S", "tu")],                   [p("R", "u"), p("A", "g̱"), p("S", "tu")]),
    ])

def subject_x():  # (xviii)
    rewrites.extend([
        ([p("A", "g̱"), p("S", "x̱")],                    [p("M", "g̱"), p("S", "x̱")]),  # (G)
    ])

def subject_x_inv():  # (xviii)^-1
    rewrites.extend([
        ([p("M", "g̱"), p("S", "x̱")],                    [p("A", "g̱"), p("S", "x̱")]),
    ])

def aspect_wu():  # (xix)
    rewrites.extend([
        ([p("Q", "a"), p("S", "i")],                    [p("Q", "a"), p("A", "wu"), p("S", "i")]),
        ([p("Q", "ka"), p("S", "i")],                   [p("Q", "ka"), p("A", "wu"), p("S", "i")]),
        ([p("Q", "x̱ʼa"), p("S", "i")],                  [p("Q", "x̱ʼe"), p("A", "wu"), p("S", "i")]),
        ([p("Q", "ji"), p("S", "i")],                   [p("Q", "ji"), p("A", "wu"), p("S", "i")]),
        ([p("Q", "tu"), p("S", "i")],                   [p("Q", "tu"), p("A", "wu"), p("S", "i")]),
        ([p("A", "e"), p("S", "e")],                    [p("Q", "a"), p("A", "wu"), p("S", "i")]),
    ])

def An2RuAn():  # (xx)
    rewrites.extend([
        ([p("A", "n")],                                 [p("R", "u"), p("A", "n")]),
    ])

def aspect_n():  # (xxi)  # number
    rewrites.extend([
        ([p("A", "n"), p("S", "yi")],                   [p("A", "n"), p("M", "g̱"), p("S", "yi")]),
        ([p("A", "n"), p("S", "du")],                   [p("A", "n"), p("M", "g̱"), p("S", "du")]),
    ])

def irrealis_u():  # (xxii)
    rewrites.extend([
        ([p("Q", "a")],                                 [p("Q", "a"), p("R", "u")]),
        ([p("Q", "ka")],                                [p("Q", "ka"), p("R", "u")]),
        ([p("Q", "x̱ʼa")],                               [p("Q", "x̱ʼe"), p("R", "u")]),
        ([p("Q", "ji")],                                [p("Q", "ji"), p("R", "u")]),
        ([p("Q", "tu")],                                [p("Q", "tu"), p("R", "u")]),
    ])

def remove_double_irrealis():  # (xxiii)
    rewrites.extend([
        ([p("R", "o"), p("R", "u")],                    [p("R", "u")]),  # Undo irrealis
        ([p("R", "u"), p("R", "u")],                    [p("R", "u")]),
        ([p("R", "e"), p("R", "u")],                    [p("R", "u")]),
        ([p("R", "i"), p("R", "u")],                    [p("R", "u")]),
    ])

def Mg2RuMg():  # (xxiv)
    rewrites.extend([
        ([p("M", "g̱")],                                 [p("R", "u"), p("M", "g̱")]),  # (F)
    ])

def Mg2RuMg_inv():  # (xxiv)^-1
    rewrites.extend([
        ([p("R", "u"), p("M", "g̱")],                    [p("M", "g̱")]),  # Undo (F)
    ])

def remove_irrealis():  # (xxv)
    rewrites.extend([
        ([p("R", "u")],                                 []),
    ])

def aspect_wu2irrealis_u():  # (xxvi)
    rewrites.extend([
        ([p("Q", "a"), p("A", "wu"), p("S", "i")],      [p("Q", "a"), p("R", "u"), p("S", "i")]),
        ([p("Q", "ka"), p("A", "wu"), p("S", "i")],     [p("Q", "ka"), p("R", "u"), p("S", "i")]),
        ([p("Q", "x̱ʼe"), p("A", "wu"), p("S", "i")],    [p("Q", "x̱ʼe"), p("R", "u"), p("S", "i")]),
        ([p("Q", "ji"), p("A", "wu"), p("S", "i")],     [p("Q", "ji"), p("R", "u"), p("S", "i")]),
        ([p("Q", "tu"), p("A", "wu"), p("S", "i")],     [p("Q", "tu"), p("R", "u"), p("S", "i")]),
    ])

def irrealis_subject():  # (xxvii)
    rewrites.extend([
        ([p("S", "tu")],                                [p("R", "u"), p("S", "tu")]),
        ([p("S", "du")],                                [p("R", "u"), p("S", "du")]),
        ([p("S", "i")],                                 [p("R", "u"), p("S", "i")]),
        ([p("S", "yeey")],                              [p("R", "u"), p("S", "yeey")]),
        ([p("S", "yi")],                                [p("R", "u"), p("S", "yi")]),
    ])

def disjunct_u():  # (xxviii) probably a mistake
    rewrites.extend([
        ([p("S", "i")],                                 [p("Q", "u"), p("S", "i")]),
    ])

# actual sequence of rewrites
remove_epenthesis()  # (i)
irreg_disjuncts()  # (ii) 
xw2wux()  # (iii)
make_RuAg()  # (iv)
gw2ug()  # (v)
s2ds()  # (vi)
gw2ug_inv()  # (v)^-1
s2ds_inv()  # (vi)^-1
Mx2Mg()  # (vii)
make_AgMg()  # (viii)
gg2wgg()  # (ix)
make_wggx() # (x)
make_ggx()  # (xi)
s2ds()  # (vi)
s2ds_inv()  # (vi)^-1
go2ug()  # (xii)
irreg_subj()  # (xiii)
make_ugdu()  # (xiv)
make_ugi()  # (xv)
make_ugyi()  # (xvi)
make_ugtu()  # (xvii)
subject_x()  # (xviii)
aspect_wu()  # (xix)
s2ds()  # (vi)
s2ds_inv()  # (vi)^-1
An2RuAn()  # (xx)
s2ds()  # (vi)
s2ds_inv()  # (vi)^-1
aspect_n()  # (xxi)
s2ds()  # (vi)
gg2wgg_inv()  # (ix)^-1
irrealis_u()  # (xxii)
remove_double_irrealis()  # (xxiii)
Mg2RuMg()  # (xxiv)
s2ds_inv() # (vi)^-1
Mg2RuMg_inv()  # (xxiv)^-1
subject_x_inv()  # (xviii)
s2ds()  # (vi)
remove_irrealis()  # (xxv)
aspect_wu2irrealis_u()  # (xxvi) -- chains with (xix)
irrealis_subject()  # (xxvii)
s2ds_inv()  # (vi)^-1
remove_irrealis()  # (xxv) -- should not be needed
disjunct_u()  # (xxviii) -- should not be needed

def pair_list_to_string(pair_list):
    ret_val = ""
    for pair in pair_list:
        ret_val += pair[1]
    return ret_val

actual_to_rewritten = {}
for k in hidden_to_observed.keys():
    #print("Underlying:", k.to_string(),"\t", "Observed: ",hidden_to_observed[k].to_string())
    #if k.same_tags(hidden_to_observed[k]):
    #    print("\tUnderlying:")
    #    k.print_verbose()
    #    print("\tObserved:")
    #    hidden_to_observed[k].print_verbose()
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
for i in range(len(rewrites)):
    for (k,v) in actual_to_rewritten.items():
        actual_to_rewritten[k] = v.replace_sublist(rewrites[i][0], rewrites[i][1])
    print(pair_list_to_string(rewrites[i][0]), "->", pair_list_to_string(rewrites[i][1]), ": removed", end=" ")
    remove_matching_tags()
    print("So far:", len(observed_to_hidden), "\t", "Rest:", len(hidden_to_observed))

for (k,v) in observed_to_hidden.items():
    pass
    #print(k, "\t", list(x.to_string() for x in v))
for (k,v) in hidden_to_observed.items():
    pass
    print(k.print_verbose(), print(), actual_to_rewritten[v].print_verbose(), v.to_string(False), sep="    ")
    #print(k.to_string(True), actual_to_rewritten[v].to_string(True), v.to_string(False), sep="    ")
