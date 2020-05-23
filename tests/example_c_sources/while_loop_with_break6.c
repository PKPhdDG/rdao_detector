#include <stdio.h>

int i=100;

int main()
{
    while(i)
    {
        if (i < 5) {
            break;
        }
        else {
            printf("%d\n", i--);
        }
    }

    return 0;
}
