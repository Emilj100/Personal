#include <cs50.h>
#include <stdio.h>

int main(void)
{
    double x = get_int("x: ");
    double y = get_int("y: ");

    printf("%.20f\n", x / y);
}

