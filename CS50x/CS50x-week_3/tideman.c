#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// Max number of candidates
#define MAX 9

// preferences[i][j] er antallet af vælgere, der foretrækker kandidat i fremfor kandidat j
int preferences[MAX][MAX];

// locked[i][j] betyder, at kandidat i er "låst" over kandidat j
bool locked[MAX][MAX];

// Kandidaterne
typedef struct
{
    int winner;
    int loser;
} pair;

// Array af kandidater
string candidates[MAX];
pair pairs[MAX * (MAX - 1) / 2];

int pair_count;
int candidate_count;

// Funktionsprototyper
void record_preferences(int ranks[]);
void add_pairs(void);
void sort_pairs(void);
void lock_pairs(void);
void print_winner(void);

bool creates_cycle(int winner, int loser);
void rank_candidates(string name, int ranks[], int rank);
bool is_source(int candidate);

int main(int argc, string argv[])
{
    // Tjek for korrekt brug
    if (argc < 2)
    {
        printf("Usage: tideman [candidate ...]\n");
        return 1;
    }

    // Antallet af kandidater
    candidate_count = argc - 1;
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }

    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i] = argv[i];
    }

    // Initialiser præferencer og locked
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            preferences[i][j] = 0;
            locked[i][j] = false;
        }
    }

    pair_count = 0;
    int voter_count = get_int("Number of voters: ");

    // Indsamling af vælgernes præferencer
    for (int i = 0; i < voter_count; i++)
    {
        int ranks[candidate_count];

        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);
            rank_candidates(name, ranks, j);
        }

        record_preferences(ranks);
    }

    add_pairs();
    sort_pairs();
    lock_pairs();
    print_winner();
    return 0;
}

// Registrér vælgerens præferencer
void record_preferences(int ranks[])
{
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = i + 1; j < candidate_count; j++)
        {
            preferences[ranks[i]][ranks[j]]++;
        }
    }
}

// Tilføj par af kandidater, der har et direkte forhold
void add_pairs(void)
{
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            if (preferences[i][j] > preferences[j][i])
            {
                pairs[pair_count].winner = i;
                pairs[pair_count].loser = j;
                pair_count++;
            }
        }
    }
}

// Sortér par baseret på styrken af sejren
void sort_pairs(void)
{
    for (int i = 0; i < pair_count - 1; i++)
    {
        for (int j = 0; j < pair_count - i - 1; j++)
        {
            int strength1 = preferences[pairs[j].winner][pairs[j].loser] - preferences[pairs[j].loser][pairs[j].winner];
            int strength2 = preferences[pairs[j + 1].winner][pairs[j + 1].loser] - preferences[pairs[j + 1].loser][pairs[j + 1].winner];
            if (strength1 < strength2)
            {
                pair temp = pairs[j];
                pairs[j] = pairs[j + 1];
                pairs[j + 1] = temp;
            }
        }
    }
}

// Lås par ind i grafen uden at skabe en cyklus
void lock_pairs(void)
{
    for (int i = 0; i < pair_count; i++)
    {
        if (!creates_cycle(pairs[i].winner, pairs[i].loser))
        {
            locked[pairs[i].winner][pairs[i].loser] = true;
        }
    }
}

// Kontroller, om tilføjelse af en kant skaber en cyklus
bool creates_cycle(int winner, int loser)
{
    if (loser == winner)
    {
        return true;
    }

    for (int i = 0; i < candidate_count; i++)
    {
        if (locked[loser][i])
        {
            if (creates_cycle(winner, i))
            {
                return true;
            }
        }
    }

    return false;
}

// Print vinderen
void print_winner(void)
{
    for (int i = 0; i < candidate_count; i++)
    {
        if (is_source(i))
        {
            printf("%s\n", candidates[i]);
            return;
        }
    }
}

// Kontroller, om en kandidat er en kilde
bool is_source(int candidate)
{
    for (int i = 0; i < candidate_count; i++)
    {
        if (locked[i][candidate])
        {
            return false;
        }
    }
    return true;
}

// Find kandidatens rangering
void rank_candidates(string name, int ranks[], int rank)
{
    for (int i = 0; i < candidate_count; i++)
    {
        if (strcmp(name, candidates[i]) == 0)
        {
            ranks[rank] = i;
            return;
        }
    }
    printf("Invalid vote.\n");
    exit(1);
}
