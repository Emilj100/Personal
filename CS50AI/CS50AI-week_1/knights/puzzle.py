from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

ASaidKnave = Symbol("A said 'I am a knave'")
ASaidKnight = Symbol("A said 'I am a knight'")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # 1. A er enten en ridder eller en knave, men ikke begge.
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    # 2. A’s udsagn er: "Jeg er både en ridder og en knave."
    #    Vi udtrykker det med: And(AKnight, AKnave)

    # 3. Hvis A er en ridder, skal hans udsagn være sandt.
    Implication(AKnight, And(AKnight, AKnave)),

    # 4. Hvis A er en knave, skal hans udsagn være falsk.
    Implication(AKnave, Not(And(AKnight, AKnave)))

    
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(

    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    Implication(AKnight, And(AKnave, BKnave)),

    Implication(AKnave, Not(And(AKnave, BKnave))),

)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    # A's udsagn: "Vi er af samme slags."
    Implication(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    Implication(AKnave, Not(Or(And(AKnight, BKnight), And(AKnave, BKnave)))),

    # B's udsagn: "Vi er af forskellige slags."
    Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),
    Implication(BKnave, Not(Or(And(AKnight, BKnave), And(AKnave, BKnight))))

)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, AKnave),
    Not(And(AKnight, AKnave)),

    Or(BKnight, BKnave),
    Not(And(BKnight, BKnave)),

    Or(CKnight, CKnave),
    Not(And(CKnight, CKnave)),

    Or(ASaidKnave, ASaidKnight),
    Not(And(ASaidKnave, ASaidKnight)),

    Implication(AKnight, ASaidKnight),
    Implication(AKnave, ASaidKnight),

    Implication(BKnight, ASaidKnave),
    Implication(BKnave, Not(ASaidKnave)),

    Implication(BKnight, CKnave),    
    Implication(BKnave, Not(CKnave)),

    Implication(CKnight, AKnight),    
    Implication(CKnave, Not(AKnight)),
    
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
