#include <stdio.h>

int main()
{
    int i=100;
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
