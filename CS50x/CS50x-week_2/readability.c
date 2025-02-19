#include <ctype.h>
#include <cs50.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    // Prompt the user for some text
    string text = get_string("Text: ");
    int sentence = 0;
    int words = 1;
    int letters = 0;

    // Count the number of letters, words, and sentences in the text
    for (int i = 0, n = strlen(text); i < n; i += 1)
    {
        text[i] = tolower(text[i]);
        if (text[i] == ' ')
        {
            words += 1;
        }
        else if (text[i] == '.' || text[i] == '!' || text[i] == '?')
        {
            sentence += 1;
        }
        else if (text[i] >= 'a' && text[i] <= 'z')
        {
            letters += 1;
        }
    }
    // Compute the Coleman-Liau index
    float L = (float) letters / words * 100;
    float S = (float) sentence / words * 100;

    float index_float = 0.0588 * L - 0.296 * S - 15.8;
    int index = round(index_float);
    // Print the grade level
    if (index < 0)
    {
        printf("Before Grade 1\n");
    }

    else if (index > 16)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %i\n", index);
    }

}
