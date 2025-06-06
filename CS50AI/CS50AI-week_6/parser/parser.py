import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S        -> NP VP
S        -> S Conj S

NP       -> Det AdjList N PPList
NP       -> AdjList N PPList
NP       -> N PPList
NP       -> NP Conj NP

AdjList  -> Adj AdjList |
PPList   -> PP PPList   |
PPList   ->

PP       -> P NP

VP       -> V NP PPList
VP       -> V PPList
VP       -> V
VP       -> VP Conj VP
VP       -> Adv VP
VP       -> VP Adv
"""


grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    all_characters = nltk.word_tokenize(sentence)

    words = []
    for token in all_characters:
        if any(char.isalpha() for char in token):
            words.append(token.lower())
        
    return words



def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    noun_phrase_chunks = []
    for subtree in tree.subtrees(lambda t: t.label()=="NP"):
        counter = 0
        for s in subtree.subtrees(lambda t: t.label()=="NP"):
            counter += 1
            if counter >= 2:
                break
            
        if counter == 1:    
            noun_phrase_chunks.append(subtree)

    return noun_phrase_chunks


if __name__ == "__main__":
    main()
