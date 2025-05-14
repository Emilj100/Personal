import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    N = len(corpus)
    result = {}
    # Hvis ikke udgående links
    if not corpus[page]:
        for page_in_corpus in corpus:
            result[page_in_corpus] = 1/N
        return result
    # Hvis udgående links
    else:
        L = len(corpus[page])
        for page_in_corpus in corpus:
            result[page_in_corpus] = (1 - damping_factor) / N
        for page_in_corpus in corpus[page]:
            result[page_in_corpus] += damping_factor / L
        return result
            


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    sampling = {}
    for page_in_corpus in corpus:
        sampling[page_in_corpus] = 0
    current_page = random.choice(list(corpus.keys()))

    for sample in range(n):
        distribution = transition_model(corpus, current_page, damping_factor)
        keys = list(distribution.keys())
        values = list(distribution.values())
        next_page = random.choices(keys, values)
        current_page = next_page[0]
        sampling[current_page] += 1

    for page in sampling:
        sampling[page] = sampling[page] / n

    return sampling


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    N = len(corpus)
    ranks = {}
    for page_in_corpus in corpus:
        ranks[page_in_corpus] = 1/N

    while True:
        new_ranks = {}

        for p in corpus:
            new_ranks[p] = (1 - damping_factor) / N
            for q in corpus:
                if p in corpus[q]:
                    if corpus[q]:
                        new_ranks[p] += damping_factor * ranks[q] / len(corpus[q])
                    else:
                        new_ranks[p] += damping_factor * ranks[q] / N

        biggest_difference = 0
        for p in corpus:
            difference = abs(new_ranks[p] - ranks[p])
            if biggest_difference < difference:
                biggest_difference = difference

        ranks = new_ranks.copy()
        
        if biggest_difference < 0.001:
            break

    return new_ranks


if __name__ == "__main__":
    main()
