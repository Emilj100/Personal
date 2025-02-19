#include <ctype.h>
#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, string argv[])
{
    if (argc == 2)
    {
        bool is_alpha = false;
        for (int i = 0, n = strlen(argv[1]); i < n; i += 1)
        {
            if (isalpha(argv[1][i]))
            {
                is_alpha = true;
                break;
            }
        }

        if (is_alpha)
        {
            printf("Enter a number\n");
            return 1;
        }

        int key = atoi(argv[1]);
        if (key > 0)
        {
            string plaintext = get_string("plaintext:  ");
            printf("ciphertext: ");
            for (int i = 0, n = strlen(plaintext); i < n; i += 1)
            {
                int rotate = 0;
                if (isupper(plaintext[i]))
                {
                    rotate += ((plaintext[i] - 'A' + key) % 26) + 'A';
                }
                else if (islower(plaintext[i]))
                {
                    rotate += ((plaintext[i] - 'a' + key) % 26) + 'a';
                }
                else
                {
                    rotate += plaintext[i];
                }

                printf("%c", rotate);
            }

            printf("\n");
            return 0;
        }
    }
    else
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
}
