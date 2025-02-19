#include <cs50.h>
#include <stdio.h>

void draw(int n);

int main(void)
{
    int height = get_int("Height: ");
    draw(height);
}

void draw(int n)
{
    // For hver række i trappen
    for (int i = 0; i < n; i += 1)
    {
        for (int j = 0; j < i + 1; j += 1)
        {
            printf("#");
        }
        printf("\n");
    }
}
