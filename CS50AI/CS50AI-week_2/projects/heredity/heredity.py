import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Beregn og returnér den samlede sandsynlighed for en given konfiguration.

    Sandsynligheden skal være den kombinerede sandsynlighed for, at:
      * alle i mængden 'one_gene' har præcis én kopi af genet,
      * alle i mængden 'two_genes' har præcis to kopier af genet,
      * alle, der hverken er i 'one_gene' eller 'two_genes', har 0 kopier,
      * alle i mængden 'have_trait' udviser det givne træk,
      * alle, der ikke er i 'have_trait', ikke udviser træk.
    """
    # Start med en samlet sandsynlighed på 1 (produktet af alle individuelle sandsynligheder)
    joint_prob = 1

    # Gennemløb alle personer i datasættet
    for person in people:
        # Bestem antallet af genkopier for personen baseret på de givne mængder
        if person in one_gene:
            gene_count = 1
        elif person in two_genes:
            gene_count = 2
        else:
            gene_count = 0

        # Bestem, om personen udviser trait: True hvis personen er med i have_trait, ellers False
        has_trait = (person in have_trait)

        # Hvis personen ikke har angivne forældre, bruges de ubetingede sandsynligheder
        if not people[person]["mother"] and not people[person]["father"]:
            gene_prob = PROBS["gene"][gene_count]
        else:
            # Hvis personen har forældreinformation, skal vi beregne nedarvningssandsynligheden

            # Bestem moderens genetilstand (antal kopier)
            if people[person]["mother"]:
                if people[person]["mother"] in one_gene:
                    mother_gene_count = 1
                elif people[person]["mother"] in two_genes:
                    mother_gene_count = 2
                else:
                    mother_gene_count = 0

            # Bestem faderens genetilstand (antal kopier)
            if people[person]["father"]:
                if people[person]["father"] in one_gene:
                    father_gene_count = 1
                elif people[person]["father"] in two_genes:
                    father_gene_count = 2
                else:
                    father_gene_count = 0

            # Konverter moderens genetilstand til en transmissionssandsynlighed
            if mother_gene_count == 2:
                p_mother = 1 - PROBS["mutation"]
            elif mother_gene_count == 1:
                p_mother = 0.5
            else:
                p_mother = PROBS["mutation"]

            # Konverter faderens genetilstand til en transmissionssandsynlighed
            if father_gene_count == 2:
                p_father = 1 - PROBS["mutation"]
            elif father_gene_count == 1:
                p_father = 0.5
            else:
                p_father = PROBS["mutation"]

            # Beregn barnets sandsynlighed for at modtage et bestemt antal kopier ud fra forældrenes bidrag:
            if gene_count == 0:
                # Barnet skal modtage 0 kopier: Begge forældre må undlade at give genet
                gene_prob = (1 - p_mother) * (1 - p_father)
            elif gene_count == 1:
                # Barnet skal modtage 1 kopi: Der er to muligheder (enten moderen giver og faderen ikke, eller omvendt)
                gene_prob = p_mother * (1 - p_father) + (1 - p_mother) * p_father
            else:
                # Barnet skal modtage 2 kopier: Begge forældre skal give genet
                gene_prob = p_mother * p_father

        # Hent sandsynligheden for, at personen udviser (eller ikke udviser) trait baseret på deres antal genkopier
        trait_prob = PROBS["trait"][gene_count][has_trait]
        
        # Opdater den samlede joint probability med denne persons bidrag (gen sandsynlighed * trait sandsynlighed)
        joint_prob *= gene_prob * trait_prob

    # Returnér den samlede joint probability for hele konfigurationen
    return joint_prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene: 
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p

        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else: 
            probabilities[person]["trait"][False] += p



def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        all_values_gene = sum(probabilities[person]["gene"].values())
        probabilities[person]["gene"][0] = probabilities[person]["gene"][0] / all_values_gene
        probabilities[person]["gene"][1] = probabilities[person]["gene"][1] / all_values_gene
        probabilities[person]["gene"][2] = probabilities[person]["gene"][2] / all_values_gene
        
        all_values_trait = sum(probabilities[person]["trait"].values())
        probabilities[person]["trait"][True] = probabilities[person]["trait"][True]/ all_values_trait
        probabilities[person]["trait"][False] = probabilities[person]["trait"][False]/ all_values_trait



if __name__ == "__main__":
    main()
