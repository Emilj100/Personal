#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // Få kreditkortnummeret fra brugeren
    long card_number = get_long("Number: ");
    
    // Kopier kortnummeret til en variabel, så vi kan bearbejde det
    long n = card_number;
    int sum = 0;
    int digit_count = 0;

    // Beregn summen ved hjælp af Luhn's algoritme
    while (n > 0)
    {
        // Få det sidste ciffer
        int digit = n % 10;

        // Hvert andet ciffer skal ganges med 2
        if (digit_count % 2 == 1)
        {
            digit *= 2;
            // Hvis resultatet er to cifre, læg dem sammen
            if (digit > 9)
            {
                digit = (digit % 10) + (digit / 10);
            }
        }
        
        // Læg resultatet til summen
        sum += digit;
        
        // Fjern det sidste ciffer og tæller antal cifre
        n /= 10;
        digit_count++;
    }

    // Kontroller om kortet er gyldigt ifølge Luhn's algoritme
    if (sum % 10 == 0)
    {
        // Find det første ciffer eller de første to cifre for at bestemme korttypen
        long first_two_digits = card_number;
        while (first_two_digits >= 100)
        {
            first_two_digits /= 10;
        }

        // Visa: 13 eller 16 cifre og begynder med 4
        if ((digit_count == 13 || digit_count == 16) && (first_two_digits / 10 == 4))
        {
            printf("VISA\n");
        }
        // American Express: 15 cifre og begynder med 34 eller 37
        else if (digit_count == 15 && (first_two_digits == 34 || first_two_digits == 37))
        {
            printf("AMEX\n");
        }
        // MasterCard: 16 cifre og begynder med 51, 52, 53, 54 eller 55
        else if (digit_count == 16 && (first_two_digits >= 51 && first_two_digits <= 55))
        {
            printf("MASTERCARD\n");
        }
        // Hvis ingen af ovenstående betingelser er opfyldt, er kortet ugyldigt
        else
        {
            printf("INVALID\n");
        }
    }
    else
    {
        printf("INVALID\n");
    }
}
