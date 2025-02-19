#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        return 1;
    }

    FILE *card = fopen(argv[1], "r");
    if (card == NULL)
    {
        return 1;
    }

    BYTE buffer[512];
    char filename[8];
    FILE *currentfile = NULL;
    int fileIndex = 0;

    while (fread(buffer, 1, 512, card) == 512)
    {

        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {

            if (currentfile != NULL)
            {
                fclose(currentfile);
            }

            sprintf(filename, "%03i.jpg", fileIndex);
            currentfile = fopen(filename, "w");
            fileIndex += 1;
        }

        if (currentfile != NULL)
        {
            fwrite(buffer, 1, 512, currentfile);
        }
    }

    if (currentfile != NULL)
    {
        fclose(currentfile);
    }

    fclose(card);

    return 0;
}
