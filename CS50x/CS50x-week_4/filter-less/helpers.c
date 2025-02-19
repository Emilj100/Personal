#include "helpers.h"
#include <stdio.h>
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{

    // Loop over all pixels
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Take average of red, green, and blue
            int red = image[i][j].rgbtRed;
            int green = image[i][j].rgbtGreen;
            int blue = image[i][j].rgbtBlue;

            // Update pixel values
            int average = round((red + green + blue) / 3.0);
            image[i][j].rgbtRed = average;
            image[i][j].rgbtGreen = average;
            image[i][j].rgbtBlue = average;

        }
    }

    return;
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
     // Loop over all pixels
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Compute sepia values
            int sepiaRed = round(.393 * image[i][j].rgbtRed + .769 * image[i][j].rgbtGreen + .189 * image[i][j].rgbtBlue);
            int sepiaGreen = round(.349 * image[i][j].rgbtRed + .686 * image[i][j].rgbtGreen + .168 * image[i][j].rgbtBlue);
            int sepiaBlue = round(.272 * image[i][j].rgbtRed + .534 * image[i][j].rgbtGreen + .131 * image[i][j].rgbtBlue);

            if (sepiaRed > 255)
            {
                sepiaRed = 255;
            }
            if (sepiaGreen > 255)
            {
                sepiaGreen = 255;
            }
            if (sepiaBlue > 255)
            {
                sepiaBlue = 255;
            }

            // Update pixel with sepia values
            image[i][j].rgbtRed = sepiaRed;
            image[i][j].rgbtGreen = sepiaGreen;
            image[i][j].rgbtBlue = sepiaBlue;

        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    // Loop over all pixels
    int center = width / 2;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < center; j++)
        {
            RGBTRIPLE tmp = image[i][j];
            image[i][j] = image[i][width - j - 1];
            image[i][width - j - 1] = tmp;
        }
    }
    return;
}


// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    // Lav en kopi af billedet én gang i starten
    RGBTRIPLE copy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j] = image[i][j];
        }
    }

    // Gennemgå hver pixel i billedet
    for (int i = 0; i < height; i++) // Rækker
    {
        for (int j = 0; j < width; j++) // Kolonner
        {
            int total_red = 0, total_green = 0, total_blue = 0;
            int count = 0;

            // Iterer gennem nabolaget
            for (int ii = -1; ii <= 1; ii++) // Række-offset
            {
                for (int jj = -1; jj <= 1; jj++) // Kolonne-offset
                {
                    int ni = i + ii;
                    int nj = j + jj;

                    // Tjek om (ni, nj) er inden for billedets grænser
                    if (ni >= 0 && ni < height && nj >= 0 && nj < width)
                    {
                        total_red += copy[ni][nj].rgbtRed;
                        total_green += copy[ni][nj].rgbtGreen;
                        total_blue += copy[ni][nj].rgbtBlue;
                        count += 1;
                    }
                }
            }

            // Beregn gennemsnittet og opdater den originale pixel
            image[i][j].rgbtRed = round((float)total_red / count);
            image[i][j].rgbtGreen = round((float)total_green / count);
            image[i][j].rgbtBlue = round((float)total_blue / count);
        }
    }
}
