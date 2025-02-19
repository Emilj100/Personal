#include <cs50.h>
#include <stdio.h>

// Funktion til at udskrive én linje af dobbelt-pyramiden
void print_p(int i, int height)
{
    // Beregn antal hash (#) og mellemrum for linjen
    int hc = i + 1;         // Antal hashes i denne linje (starter ved 1, stiger pr. linje)
    int sc = height - (i + 1); // Antal mellemrum før pyramiden (færre pr. linje)

    // Udskriv mellemrum før den venstre pyramide
    for (int j = 0; j < sc; j++)
    {
        putc(' ', stdout);  // Udskriv et mellemrum
    }

    // Udskriv hashes for venstre pyramide
    for (int j = 0; j < hc; j++)
    {
        putc('#', stdout);  // Udskriv et hash-tegn
    }

    // Udskriv mellemrum mellem venstre og højre pyramide
    putc(' ', stdout);
    putc(' ', stdout);

    // Udskriv hashes for højre pyramide
    for (int j = 0; j < hc; j++)
    {
        putc('#', stdout);  // Udskriv et hash-tegn
    }
}

// Hovedfunktionen
int main(void)
{
    int height;

    // Bed brugeren om en gyldig højde mellem 1 og 8
    do
    {
        height = get_int("Height: ");
    } while (height < 1 || height > 8);

    // Loop gennem hver linje for at bygge pyramiden
    for (int i = 0; i < height; i++)
    {
        print_p(i, height); // Kald print_p-funktionen for at udskrive linjen
        printf("\n");       // Udskriv ny linje for næste linje i pyramiden
    }
}

