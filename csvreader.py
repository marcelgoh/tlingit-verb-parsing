import csv
import enum
import re

hidden_to_observed = {}

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
                        hidden_to_observed[hidden] = observed

for (k,v) in hidden_to_observed.items():
    if len(k.seq) != len(v.seq):
        print(k.to_string(True), v.to_string(False), sep="    ")
